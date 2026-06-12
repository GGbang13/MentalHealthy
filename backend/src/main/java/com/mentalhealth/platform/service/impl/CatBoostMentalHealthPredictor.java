package com.mentalhealth.platform.service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mentalhealth.platform.config.MlModelProperties;
import com.mentalhealth.platform.vo.RiskFactorVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
@RequiredArgsConstructor
public class CatBoostMentalHealthPredictor {
    private static final String MODEL_NAME = "CatBoost-Mental-Risk-v1";
    private static final double DEFAULT_MAX_SCORE = 4D;
    private final MlModelProperties mlModelProperties;
    private final ObjectMapper objectMapper;

    public PredictionResult predict(String scaleCode, Map<String, Object> features) {
        PredictionResult modelPrediction = predictWithPython(scaleCode, features);
        if (modelPrediction != null) {
            return modelPrediction;
        }

        ModelProfile profile = resolveProfile(scaleCode);
        double logit = profile.baseScore();
        List<RiskFactorVO> factors = new ArrayList<>();

        for (FeatureProfile feature : profile.features().values()) {
            double value = clamp(numericFeature(features, feature.key()), 0D, feature.maxScore());
            double normalized = feature.maxScore() == 0D ? 0D : value / feature.maxScore();
            double contribution = normalized * feature.weight();
            logit += contribution;
            factors.add(buildFactor(feature, value, contribution));
        }

        logit += applyInteraction(profile.code(), features);

        double probability = sigmoid(logit) * 100D;
        int score = (int) Math.round(probability);
        String level = resolveLevel(probability);
        List<RiskFactorVO> leadingFactors = factors.stream()
            .filter(item -> item.getContributionScore() > 0D)
            .sorted(Comparator.comparing(RiskFactorVO::getContributionScore).reversed())
            .limit(5)
            .toList();

        return new PredictionResult(
            score,
            round(probability),
            level,
            MODEL_NAME,
            leadingFactors,
            buildAnalysis(level, leadingFactors)
        );
    }

    private PredictionResult predictWithPython(String scaleCode, Map<String, Object> features) {
        if (!mlModelProperties.isEnabled()) {
            return null;
        }
        try {
            Path artifactsDir = Path.of(mlModelProperties.getArtifactsDir());
            if (isMhpScale(scaleCode)) {
                return predictMhpWithPython(scaleCode, features, artifactsDir);
            }

            Path scriptPath = Path.of(mlModelProperties.getScriptPath());
            Path modelPath = artifactsDir.resolve(scaleCode.toLowerCase()).resolve(scaleCode.toLowerCase() + "_catboost_model.cbm");

            if (!Files.exists(scriptPath) || !Files.exists(modelPath)) {
                return null;
            }

            ProcessBuilder processBuilder = new ProcessBuilder(
                mlModelProperties.getPythonCommand(),
                scriptPath.toString(),
                "--scale",
                scaleCode,
                "--artifacts-dir",
                artifactsDir.toString(),
                "--features-json",
                objectMapper.writeValueAsString(features)
            );
            Process process = processBuilder.start();
            boolean finished = process.waitFor(mlModelProperties.getTimeoutSeconds(), TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                log.warn("CatBoost python inference timed out for scale {}", scaleCode);
                return null;
            }

            String stdout = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
            String stderr = new String(process.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);
            if (process.exitValue() != 0) {
                log.warn("CatBoost python inference failed for scale {}: {}", scaleCode, stderr);
                return null;
            }

            return parsePythonPrediction(stdout);
        } catch (Exception exception) {
            log.warn("CatBoost python inference unavailable for scale {}: {}", scaleCode, exception.getMessage());
            return null;
        }
    }

    private PredictionResult predictMhpWithPython(String scaleCode, Map<String, Object> features, Path artifactsDir) throws Exception {
        String target = resolveMhpTarget(scaleCode);
        Path scriptPath = Path.of("../ml/scripts/predict_mhp_catboost.py");
        Path modelPath = artifactsDir.resolve("mhp_catboost_" + target + ".cbm");
        Path schemaPath = artifactsDir.resolve("mhp_feature_schema_" + target + ".json");

        if (!Files.exists(scriptPath) || !Files.exists(modelPath) || !Files.exists(schemaPath)) {
            return null;
        }

        ProcessBuilder processBuilder = new ProcessBuilder(
            mlModelProperties.getPythonCommand(),
            scriptPath.toString(),
            "--target",
            target,
            "--artifacts-dir",
            artifactsDir.toString(),
            "--features-json",
            objectMapper.writeValueAsString(features)
        );
        Process process = processBuilder.start();
        boolean finished = process.waitFor(mlModelProperties.getTimeoutSeconds(), TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            log.warn("MHP CatBoost python inference timed out for scale {}", scaleCode);
            return null;
        }

        String stdout = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        String stderr = new String(process.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);
        if (process.exitValue() != 0) {
            log.warn("MHP CatBoost python inference failed for scale {}: {}", scaleCode, stderr);
            return null;
        }

        return parsePythonPrediction(stdout);
    }

    private PredictionResult parsePythonPrediction(String stdout) throws Exception {
        JsonNode root = objectMapper.readTree(stdout);
        return new PredictionResult(
            root.path("score").asInt(),
            round(root.path("riskProbability").asDouble()),
            root.path("resultLevel").asText("LOW"),
            root.path("modelName").asText(MODEL_NAME),
            parseFactors(root.path("leadingFactors")),
            root.path("analysis").asText("")
        );
    }

    private List<RiskFactorVO> parseFactors(JsonNode factorsNode) {
        List<RiskFactorVO> factors = new ArrayList<>();
        if (factorsNode == null || !factorsNode.isArray()) {
            return factors;
        }
        for (JsonNode node : factorsNode) {
            RiskFactorVO factor = new RiskFactorVO();
            factor.setKey(node.path("key").asText());
            factor.setName(node.path("name").asText());
            factor.setValue(round(node.path("value").asDouble()));
            factor.setContributionScore(round(node.path("contributionScore").asDouble()));
            factor.setDirection(node.path("direction").asText("RISK"));
            factor.setDescription(node.path("description").asText());
            factors.add(factor);
        }
        return factors;
    }

    private RiskFactorVO buildFactor(FeatureProfile feature, double value, double contribution) {
        RiskFactorVO factor = new RiskFactorVO();
        factor.setKey(feature.key());
        factor.setName(feature.name());
        factor.setValue(round(value));
        factor.setContributionScore(round(Math.abs(contribution) * 100D));
        factor.setDirection(contribution >= 0D ? "RISK" : "PROTECTIVE");
        factor.setDescription(feature.description());
        return factor;
    }

    private double applyInteraction(String scaleCode, Map<String, Object> features) {
        if ("PHQ9".equalsIgnoreCase(scaleCode)) {
            return normalized(features, "sleepProblem") * normalized(features, "fatigue") * 0.8D
                + normalized(features, "socialWithdrawal") * normalized(features, "selfWorthLow") * 0.7D;
        }
        return normalized(features, "uncontrollableWorry") * normalized(features, "restlessness") * 0.7D
            + normalized(features, "workPressure") * normalized(features, "familyConflict") * 0.6D;
    }

    private double normalized(Map<String, Object> features, String key) {
        return clamp(numericFeature(features, key), 0D, DEFAULT_MAX_SCORE) / DEFAULT_MAX_SCORE;
    }

    private double numericFeature(Map<String, Object> features, String key) {
        Object value = features.get(key);
        if (value instanceof Number number) {
            return number.doubleValue();
        }
        if (value instanceof String text) {
            try {
                return Double.parseDouble(text);
            } catch (NumberFormatException ignored) {
                return 0D;
            }
        }
        return 0D;
    }

    private boolean isMhpScale(String scaleCode) {
        return scaleCode != null && scaleCode.toUpperCase().startsWith("MHP_");
    }

    private String resolveMhpTarget(String scaleCode) {
        return switch (scaleCode.toUpperCase()) {
            case "MHP_DEPRESSION_RISK" -> "depression_risk";
            case "MHP_ANXIETY_RISK" -> "anxiety_risk";
            case "MHP_STRESS_RISK" -> "stress_risk";
            default -> "mental_risk";
        };
    }

    private String resolveLevel(double probability) {
        if (probability < 35D) {
            return "LOW";
        }
        if (probability < 65D) {
            return "MEDIUM";
        }
        return "HIGH";
    }

    private String buildAnalysis(String level, List<RiskFactorVO> leadingFactors) {
        String factorSummary = leadingFactors.isEmpty()
            ? "当前未识别到明显高风险驱动变量。"
            : "主要风险变量包括" + leadingFactors.stream()
                .limit(3)
                .map(RiskFactorVO::getName)
                .reduce((left, right) -> left + "、" + right)
                .orElse("暂无");
        return switch (level) {
            case "LOW" -> factorSummary + "，整体风险较低，建议保持规律作息与社会支持。";
            case "MEDIUM" -> factorSummary + "，已出现中等风险，建议尽快开展睡眠、压力与情绪管理。";
            default -> factorSummary + "，风险偏高，建议联系专业心理咨询师进一步评估。";
        };
    }

    private ModelProfile resolveProfile(String scaleCode) {
        if (isMhpScale(scaleCode)) {
            return mhpFallbackProfile();
        }
        if ("GAD7".equalsIgnoreCase(scaleCode)) {
            return gadProfile();
        }
        return phqProfile();
    }

    private ModelProfile mhpFallbackProfile() {
        Map<String, FeatureProfile> features = new LinkedHashMap<>();
        features.put("age", new FeatureProfile("age", "年龄段", "年龄段作为人口学背景变量参与筛查", 0D, DEFAULT_MAX_SCORE));
        features.put("gender", new FeatureProfile("gender", "性别", "性别作为人口学背景变量参与筛查", 0D, DEFAULT_MAX_SCORE));
        features.put("academic_year", new FeatureProfile("academic_year", "当前年级", "当前年级作为学习阶段变量参与筛查", 0D, DEFAULT_MAX_SCORE));
        return new ModelProfile("MHP_MENTAL_RISK", -1.10D, features);
    }

    private ModelProfile phqProfile() {
        Map<String, FeatureProfile> features = new LinkedHashMap<>();
        features.put("moodLow", new FeatureProfile("moodLow", "持续情绪低落", "最近两周心情低落、悲伤或空虚的程度", 1.50D, DEFAULT_MAX_SCORE));
        features.put("anhedonia", new FeatureProfile("anhedonia", "兴趣下降", "对日常活动失去兴趣或愉悦感", 1.35D, DEFAULT_MAX_SCORE));
        features.put("sleepProblem", new FeatureProfile("sleepProblem", "睡眠问题", "入睡困难、早醒或睡眠质量差", 1.20D, DEFAULT_MAX_SCORE));
        features.put("fatigue", new FeatureProfile("fatigue", "疲劳乏力", "精力不足、容易疲倦", 1.00D, DEFAULT_MAX_SCORE));
        features.put("concentrationDifficulty", new FeatureProfile("concentrationDifficulty", "注意力下降", "学习或工作时难以集中注意", 0.95D, DEFAULT_MAX_SCORE));
        features.put("selfWorthLow", new FeatureProfile("selfWorthLow", "自我评价低", "容易自责、觉得自己没有价值", 1.30D, DEFAULT_MAX_SCORE));
        features.put("socialWithdrawal", new FeatureProfile("socialWithdrawal", "社交退缩", "减少社交、回避沟通与活动", 1.05D, DEFAULT_MAX_SCORE));
        features.put("stressLoad", new FeatureProfile("stressLoad", "长期压力负荷", "学业、工作或生活压力积累程度", 0.90D, DEFAULT_MAX_SCORE));
        features.put("exerciseFrequency", new FeatureProfile("exerciseFrequency", "运动频率", "规律运动对情绪有保护作用", -0.85D, DEFAULT_MAX_SCORE));
        features.put("familySupport", new FeatureProfile("familySupport", "家庭支持", "稳定支持关系可降低心理风险", -1.10D, DEFAULT_MAX_SCORE));
        return new ModelProfile("PHQ9", -1.10D, features);
    }

    private ModelProfile gadProfile() {
        Map<String, FeatureProfile> features = new LinkedHashMap<>();
        features.put("nervousness", new FeatureProfile("nervousness", "紧张不安", "频繁感到紧张、心慌或警觉", 1.40D, DEFAULT_MAX_SCORE));
        features.put("uncontrollableWorry", new FeatureProfile("uncontrollableWorry", "无法控制担忧", "担忧想法反复出现且难以停止", 1.45D, DEFAULT_MAX_SCORE));
        features.put("irritability", new FeatureProfile("irritability", "易怒敏感", "情绪容易被触发、烦躁", 0.95D, DEFAULT_MAX_SCORE));
        features.put("restlessness", new FeatureProfile("restlessness", "坐立不安", "身体或心理上难以放松", 1.10D, DEFAULT_MAX_SCORE));
        features.put("muscleTension", new FeatureProfile("muscleTension", "肌肉紧张", "肩颈、背部或全身紧绷", 0.90D, DEFAULT_MAX_SCORE));
        features.put("sleepProblem", new FeatureProfile("sleepProblem", "睡眠问题", "睡眠受焦虑和反复思虑影响", 1.00D, DEFAULT_MAX_SCORE));
        features.put("workPressure", new FeatureProfile("workPressure", "工作学习压力", "任务截止、绩效或考试带来的压力", 1.20D, DEFAULT_MAX_SCORE));
        features.put("familyConflict", new FeatureProfile("familyConflict", "家庭冲突", "家庭关系紧张或支持不足", 1.00D, DEFAULT_MAX_SCORE));
        features.put("socialIsolation", new FeatureProfile("socialIsolation", "社会隔离", "缺乏稳定的人际支持网络", 0.85D, DEFAULT_MAX_SCORE));
        features.put("relaxationAbility", new FeatureProfile("relaxationAbility", "放松能力", "冥想、休息与自我调节能力", -0.95D, DEFAULT_MAX_SCORE));
        return new ModelProfile("GAD7", -1.00D, features);
    }

    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    private double sigmoid(double value) {
        return 1D / (1D + Math.exp(-value));
    }

    private double round(double value) {
        return Math.round(value * 100D) / 100D;
    }

    private record FeatureProfile(String key, String name, String description, double weight, double maxScore) {
    }

    private record ModelProfile(String code, double baseScore, Map<String, FeatureProfile> features) {
    }

    public record PredictionResult(
        int score,
        double riskProbability,
        String resultLevel,
        String modelName,
        List<RiskFactorVO> leadingFactors,
        String analysis
    ) {
    }
}
