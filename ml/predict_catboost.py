from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier, Pool


@dataclass(frozen=True)
class FeatureMeta:
    key: str
    name: str
    description: str


SCHEMAS = {
    "PHQ9": [
        FeatureMeta("moodLow", "持续情绪低落", "最近两周心情低落、悲伤或空虚的程度"),
        FeatureMeta("anhedonia", "兴趣下降", "对日常活动失去兴趣或愉悦感"),
        FeatureMeta("sleepProblem", "睡眠问题", "入睡困难、早醒或睡眠质量差"),
        FeatureMeta("fatigue", "疲劳乏力", "精力不足、容易疲倦"),
        FeatureMeta("concentrationDifficulty", "注意力下降", "学习或工作时难以集中注意"),
        FeatureMeta("selfWorthLow", "自我评价低", "容易自责、觉得自己没有价值"),
        FeatureMeta("socialWithdrawal", "社交退缩", "减少社交、回避沟通与活动"),
        FeatureMeta("stressLoad", "长期压力负荷", "学业、工作或生活压力积累程度"),
        FeatureMeta("exerciseFrequency", "运动频率", "规律运动对情绪有保护作用"),
        FeatureMeta("familySupport", "家庭支持", "稳定支持关系可降低心理风险"),
    ],
    "GAD7": [
        FeatureMeta("nervousness", "紧张不安", "频繁感到紧张、心慌或警觉"),
        FeatureMeta("uncontrollableWorry", "无法控制担忧", "担忧想法反复出现且难以停止"),
        FeatureMeta("irritability", "易怒敏感", "情绪容易被触发、烦躁"),
        FeatureMeta("restlessness", "坐立不安", "身体或心理上难以放松"),
        FeatureMeta("muscleTension", "肌肉紧张", "肩颈、背部或全身紧绷"),
        FeatureMeta("sleepProblem", "睡眠问题", "睡眠受焦虑和反复思虑影响"),
        FeatureMeta("workPressure", "工作学习压力", "任务截止、绩效或考试带来的压力"),
        FeatureMeta("familyConflict", "家庭冲突", "家庭关系紧张或支持不足"),
        FeatureMeta("socialIsolation", "社会隔离", "缺乏稳定的人际支持网络"),
        FeatureMeta("relaxationAbility", "放松能力", "冥想、休息与自我调节能力"),
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run inference for a trained CatBoost mental health model.")
    parser.add_argument("--scale", required=True, choices=sorted(SCHEMAS.keys()))
    parser.add_argument("--artifacts-dir", required=True, type=Path)
    parser.add_argument("--features-json")
    parser.add_argument("--features-file", type=Path)
    return parser.parse_args()


def resolve_level(probability: float) -> str:
    if probability < 35.0:
        return "LOW"
    if probability < 65.0:
        return "MEDIUM"
    return "HIGH"


def round2(value: float) -> float:
    return round(float(value), 2)


def build_analysis(level: str, leading_factors: list[dict]) -> str:
    risk_factors = [factor["name"] for factor in leading_factors if factor["direction"] == "RISK"][:3]
    if risk_factors:
        prefix = "主要风险变量包括" + "、".join(risk_factors)
    else:
        prefix = "当前未识别到明显高风险驱动变量"

    if level == "LOW":
        return prefix + "，整体风险较低，建议保持规律作息与社会支持。"
    if level == "MEDIUM":
        return prefix + "，已出现中等风险，建议尽快开展睡眠、压力与情绪管理。"
    return prefix + "，风险偏高，建议联系专业心理咨询师进一步评估。"


def main() -> None:
    args = parse_args()
    feature_meta = SCHEMAS[args.scale]
    feature_order = [item.key for item in feature_meta]
    if args.features_file:
        feature_payload = json.loads(args.features_file.read_text(encoding="utf-8"))
    elif args.features_json:
        feature_payload = json.loads(args.features_json)
    else:
        raise ValueError("Either --features-json or --features-file must be provided.")

    model_path = args.artifacts_dir / args.scale.lower() / f"{args.scale.lower()}_catboost_model.cbm"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    row = {item.key: float(feature_payload.get(item.key, 0.0)) for item in feature_meta}
    frame = pd.DataFrame([row], columns=feature_order)

    model = CatBoostClassifier()
    model.load_model(str(model_path))

    pool = Pool(frame)
    probability = float(model.predict_proba(frame)[0][1]) * 100.0
    shap_values = model.get_feature_importance(pool, type="ShapValues")[0]

    factors = []
    for index, item in enumerate(feature_meta):
        contribution = float(shap_values[index])
        factors.append(
            {
                "key": item.key,
                "name": item.name,
                "value": round2(row[item.key]),
                "contributionScore": round2(abs(contribution) * 100.0),
                "direction": "RISK" if contribution >= 0 else "PROTECTIVE",
                "description": item.description,
            }
        )

    leading_factors = sorted(factors, key=lambda factor: factor["contributionScore"], reverse=True)[:5]
    level = resolve_level(probability)

    result = {
        "score": int(round(probability)),
        "riskProbability": round2(probability),
        "resultLevel": level,
        "modelName": "CatBoost-RealModel-v1",
        "leadingFactors": leading_factors,
        "analysis": build_analysis(level, leading_factors),
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
