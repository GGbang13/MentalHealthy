from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
from catboost import CatBoostClassifier, Pool

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACTS_DIR = ROOT / "ml" / "artifacts"
TARGETS = ["depression_risk", "anxiety_risk", "stress_risk", "mental_risk"]

FEATURE_LABELS = {
    "age": "年龄段",
    "gender": "性别",
    "university": "学校",
    "department": "院系方向",
    "academic_year": "当前年级",
    "current_cgpa": "当前 CGPA",
    "waiver_or_scholarship": "奖助学金情况",
}


def load_json_payload(features_json: str | None, features_file: Path | None) -> dict[str, Any]:
    if features_file:
        return json.loads(features_file.read_text(encoding="utf-8"))
    if features_json:
        return json.loads(features_json)
    raise ValueError("Either --features-json or --features-file must be provided.")


def load_schema(target: str, artifacts_dir: Path) -> dict:
    schema_path = artifacts_dir / f"mhp_feature_schema_{target}.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Feature schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def prepare_frame(payload: dict[str, Any], schema: dict) -> pd.DataFrame:
    row = {}
    categorical = set(schema.get("categorical_features", []))
    for feature in schema["features"]:
        value = payload.get(feature)
        if feature in categorical:
            row[feature] = "__missing__" if value is None or str(value).strip() == "" else str(value)
        else:
            row[feature] = pd.to_numeric(pd.Series([value]), errors="coerce").fillna(0).iloc[0]
    return pd.DataFrame([row], columns=schema["features"])


def resolve_level(probability: float) -> str:
    if probability < 35.0:
        return "LOW"
    if probability < 65.0:
        return "MEDIUM"
    return "HIGH"


def level_label(level: str) -> str:
    if level == "LOW":
        return "较低风险"
    if level == "MEDIUM":
        return "中等风险"
    return "较高风险"


def direction(contribution: float) -> str:
    return "RISK" if contribution >= 0 else "PROTECTIVE"


def factor_description(feature: str, value: Any, item_direction: str) -> str:
    label = FEATURE_LABELS.get(feature, feature)
    if item_direction == "RISK":
        return f"{label}在当前模型中提高了本次心理健康风险筛查概率。"
    return f"{label}在当前模型中降低或缓冲了本次心理健康风险筛查概率。"


def build_analysis(level: str, leading_factors: list[dict]) -> str:
    if level == "HIGH":
        recommendation = "建议进一步咨询专业人员。"
    elif level == "MEDIUM":
        recommendation = "建议持续关注近期状态，必要时进一步咨询专业人员。"
    else:
        recommendation = "建议保持规律作息和稳定支持。"
    factor_text = "、".join(factor["name"] for factor in leading_factors[:3]) if leading_factors else "暂无明显单项因素"
    return f"心理健康风险筛查结果为{level_label(level)}，主要参考因素包括{factor_text}。{recommendation}"


def predict(target: str, payload: dict[str, Any], artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR) -> dict:
    schema = load_schema(target, artifacts_dir)
    model_path = artifacts_dir / f"mhp_catboost_{target}.cbm"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    frame = prepare_frame(payload, schema)
    pool = Pool(frame, cat_features=schema.get("categorical_features", []))

    model = CatBoostClassifier()
    model.load_model(str(model_path))
    probability = float(model.predict_proba(pool)[0][1]) * 100.0
    shap_values = model.get_feature_importance(pool, type="ShapValues")[0][:-1]

    factors = []
    for index, feature in enumerate(schema["features"]):
        contribution = float(shap_values[index])
        item_direction = direction(contribution)
        factors.append(
            {
                "key": feature,
                "name": FEATURE_LABELS.get(feature, feature),
                "value": frame.iloc[0][feature].item() if hasattr(frame.iloc[0][feature], "item") else frame.iloc[0][feature],
                "contributionScore": round(abs(contribution) * 100.0, 2),
                "direction": item_direction,
                "description": factor_description(feature, frame.iloc[0][feature], item_direction),
            }
        )
    leading_factors = sorted(factors, key=lambda item: item["contributionScore"], reverse=True)[:5]
    level = resolve_level(probability)
    return {
        "score": int(round(probability)),
        "riskProbability": round(probability, 2),
        "resultLevel": level,
        "resultLabel": level_label(level),
        "screeningName": "心理健康风险筛查",
        "modelName": "MHP-CatBoost-Mental-Risk",
        "leadingFactors": leading_factors,
        "analysis": build_analysis(level, leading_factors),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MHP CatBoost risk screening inference.")
    parser.add_argument("--target", default="mental_risk", choices=TARGETS)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--features-json")
    parser.add_argument("--features-file", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = load_json_payload(args.features_json, args.features_file)
    print(json.dumps(predict(args.target, payload, args.artifacts_dir), ensure_ascii=False))


if __name__ == "__main__":
    main()
