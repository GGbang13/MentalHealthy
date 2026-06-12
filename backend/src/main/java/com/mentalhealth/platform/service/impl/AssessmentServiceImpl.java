package com.mentalhealth.platform.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.mentalhealth.platform.common.BusinessException;
import com.mentalhealth.platform.dto.AssessmentSubmitRequest;
import com.mentalhealth.platform.entity.AssessmentRecord;
import com.mentalhealth.platform.entity.AssessmentScale;
import com.mentalhealth.platform.entity.User;
import com.mentalhealth.platform.mapper.AssessmentRecordMapper;
import com.mentalhealth.platform.mapper.AssessmentScaleMapper;
import com.mentalhealth.platform.mapper.UserMapper;
import com.mentalhealth.platform.service.AssessmentService;
import com.mentalhealth.platform.vo.AssessmentMonitorRecordVO;
import com.mentalhealth.platform.vo.RiskFactorVO;
import lombok.extern.slf4j.Slf4j;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class AssessmentServiceImpl implements AssessmentService {
    private final AssessmentScaleMapper assessmentScaleMapper;
    private final AssessmentRecordMapper assessmentRecordMapper;
    private final UserMapper userMapper;
    private final CatBoostMentalHealthPredictor predictor;
    private final ObjectMapper objectMapper;

    @Override
    public List<AssessmentScale> listScales() {
        return assessmentScaleMapper.selectList(new LambdaQueryWrapper<AssessmentScale>()
            .eq(AssessmentScale::getEnabled, 1));
    }

    @Override
    public AssessmentRecord submit(Long userId, AssessmentSubmitRequest request) {
        AssessmentScale scale = assessmentScaleMapper.selectById(request.getScaleId());
        if (scale == null || scale.getEnabled() == null || scale.getEnabled() != 1) {
            throw new BusinessException("量表不存在或已停用");
        }

        try {
            Map<String, Object> features = parseFeatures(request.getAnswerJson());
            CatBoostMentalHealthPredictor.PredictionResult prediction = predictor.predict(scale.getCode(), features);

            AssessmentRecord record = new AssessmentRecord();
            record.setUserId(userId);
            record.setScaleId(request.getScaleId());
            record.setAnswerJson(request.getAnswerJson());
            record.setStatus(request.getStatus() == null ? "COMPLETED" : request.getStatus());
            record.setScore(prediction.score());
            record.setRiskProbability(prediction.riskProbability());
            record.setResultLevel(prediction.resultLevel());
            record.setAnalysis(prediction.analysis());
            record.setModelName(prediction.modelName());
            record.setLeadingFactors(prediction.leadingFactors());
            record.setLeadingFactorsJson(writeFactors(prediction.leadingFactors()));
            assessmentRecordMapper.insert(record);
            return record;
        } catch (BusinessException exception) {
            throw exception;
        } catch (Exception exception) {
            log.error("Assessment submit failed. userId={}, scaleId={}", userId, request.getScaleId(), exception);
            throw new BusinessException("测评结果保存失败，请检查数据库表结构与后端日志");
        }
    }

    @Override
    public List<AssessmentRecord> history(Long userId) {
        List<AssessmentRecord> records = assessmentRecordMapper.selectList(new LambdaQueryWrapper<AssessmentRecord>()
            .eq(AssessmentRecord::getUserId, userId)
            .orderByDesc(AssessmentRecord::getCreatedAt));
        records.forEach(record -> record.setLeadingFactors(readFactors(record.getLeadingFactorsJson())));
        return records;
    }

    @Override
    public List<AssessmentMonitorRecordVO> adminRecords(Long operatorId) {
        assertAdmin(operatorId);
        List<AssessmentRecord> records = assessmentRecordMapper.selectList(new LambdaQueryWrapper<AssessmentRecord>()
            .orderByDesc(AssessmentRecord::getCreatedAt));
        return records.stream().map(this::toMonitorRecord).toList();
    }

    private Map<String, Object> parseFeatures(String answerJson) {
        if (answerJson == null || answerJson.isBlank()) {
            return Collections.emptyMap();
        }
        try {
            return objectMapper.readValue(answerJson, new TypeReference<>() {});
        } catch (Exception exception) {
            throw new BusinessException("测评数据格式错误，请使用 JSON 提交变量分值");
        }
    }

    private String writeFactors(List<RiskFactorVO> factors) {
        try {
            return objectMapper.writeValueAsString(factors);
        } catch (Exception exception) {
            throw new BusinessException("风险变量结果序列化失败");
        }
    }

    private List<RiskFactorVO> readFactors(String factorsJson) {
        if (factorsJson == null || factorsJson.isBlank()) {
            return List.of();
        }
        try {
            return objectMapper.readValue(factorsJson, new TypeReference<>() {});
        } catch (Exception exception) {
            return List.of();
        }
    }

    private AssessmentMonitorRecordVO toMonitorRecord(AssessmentRecord record) {
        AssessmentMonitorRecordVO vo = new AssessmentMonitorRecordVO();
        vo.setId(record.getId());
        vo.setUserId(record.getUserId());
        vo.setScaleId(record.getScaleId());
        vo.setScore(record.getScore());
        vo.setRiskProbability(record.getRiskProbability());
        vo.setResultLevel(record.getResultLevel());
        vo.setAnalysis(record.getAnalysis());
        vo.setModelName(record.getModelName());
        vo.setStatus(record.getStatus());
        vo.setCreatedAt(record.getCreatedAt());

        User user = userMapper.selectById(record.getUserId());
        if (user != null) {
            vo.setUsername(user.getUsername());
            vo.setNickname(user.getNickname());
        }

        AssessmentScale scale = assessmentScaleMapper.selectById(record.getScaleId());
        if (scale != null) {
            vo.setScaleName(scale.getName());
        }

        return vo;
    }

    private void assertAdmin(Long operatorId) {
        User operator = userMapper.selectById(operatorId);
        if (operator == null || !"ADMIN".equals(operator.getRole())) {
            throw new BusinessException("当前账号没有管理权限");
        }
    }
}
