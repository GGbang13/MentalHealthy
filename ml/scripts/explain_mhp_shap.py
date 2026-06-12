from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier, Pool

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = ROOT / "ml" / "data" / "mhp_university_students" / "processed" / "mhp_model_dataset.csv"
DEFAULT_OUTPUT_DIR = ROOT / "ml" / "artifacts"
TARGETS = ["depression_risk", "anxiety_risk", "stress_risk", "mental_risk"]


def load_schema(artifacts_dir: Path, target: str) -> dict:
    schema_path = artifacts_dir / f"mhp_feature_schema_{target}.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Feature schema not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def prepare_features(frame: pd.DataFrame, schema: dict) -> pd.DataFrame:
    features = frame.loc[:, schema["features"]].copy()
    categorical = set(schema.get("categorical_features", []))
    for column in features.columns:
        if column in categorical:
            features[column] = features[column].fillna("__missing__").astype(str)
        else:
            features[column] = pd.to_numeric(features[column], errors="coerce")
            if features[column].isna().any():
                features[column] = features[column].fillna(features[column].median())
    return features


def user_friendly_label(feature: str) -> str:
    replacements = {
        "phq": "PHQ",
        "gad": "GAD",
        "pss": "PSS",
        "gpa": "GPA",
    }
    words = []
    for item in feature.split("_"):
        words.append(replacements.get(item, item.capitalize()))
    return " ".join(words)


def direction_summary(mean_shap: float) -> str:
    if mean_shap > 0.001:
        return "higher_values_tend_to_raise_screening_risk"
    if mean_shap < -0.001:
        return "higher_values_tend_to_lower_screening_risk"
    return "mixed_or_low_directional_effect"


def explain(args: argparse.Namespace) -> list[dict]:
    schema = load_schema(args.artifacts_dir, args.target)
    model_path = args.artifacts_dir / f"mhp_catboost_{args.target}.cbm"
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    frame = pd.read_csv(args.data)
    features = prepare_features(frame, schema)
    pool = Pool(features, cat_features=schema.get("categorical_features", []))

    model = CatBoostClassifier()
    model.load_model(str(model_path))
    shap_values = model.get_feature_importance(pool, type="ShapValues")
    feature_shap = shap_values[:, :-1]

    rows = []
    for index, feature in enumerate(schema["features"]):
        values = feature_shap[:, index]
        rows.append(
            {
                "feature": feature,
                "importance": round(float(abs(values).mean()), 6),
                "direction_summary": direction_summary(float(values.mean())),
                "user_friendly_label": user_friendly_label(feature),
            }
        )
    rows = sorted(rows, key=lambda item: item["importance"], reverse=True)[: args.top_n]

    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.artifacts_dir / f"mhp_shap_global_{args.target}.json"
    output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Explain a trained MHP CatBoost model with global SHAP importance.")
    parser.add_argument("--target", required=True, choices=TARGETS)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--top-n", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(explain(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
