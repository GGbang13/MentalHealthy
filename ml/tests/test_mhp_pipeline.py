from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def test_prepare_mhp_dataset_normalizes_columns_and_builds_risk_targets(tmp_path: Path) -> None:
    from ml.scripts.prepare_mhp_dataset import prepare_dataset

    raw_path = tmp_path / "mhp_dataset.csv"
    processed_path = tmp_path / "mhp_model_dataset.csv"
    metadata_path = tmp_path / "mhp_model_metadata.json"
    pd.DataFrame(
        [
            {
                "Age": 20,
                "Gender": "Female",
                "Academic Year": "2nd",
                "PHQ-9 Score": 12,
                "GAD 7 Score": 4,
                "PSS-10 Score": 25,
            },
            {
                "Age": 22,
                "Gender": "Male",
                "Academic Year": "4th",
                "PHQ-9 Score": 3,
                "GAD 7 Score": 11,
                "PSS-10 Score": 10,
            },
        ]
    ).to_csv(raw_path, index=False)

    metadata = prepare_dataset(raw_path, processed_path, metadata_path)

    processed = pd.read_csv(processed_path)
    assert "academic_year" in processed.columns
    assert "phq_9_score" in processed.columns
    assert processed["depression_risk"].tolist() == [1, 0]
    assert processed["anxiety_risk"].tolist() == [0, 1]
    assert processed["stress_risk"].tolist() == [1, 0]
    assert processed["mental_risk"].tolist() == [1, 1]

    saved_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata == saved_metadata
    assert "phq_9_score" in metadata["excluded_leakage_features"]["depression_risk"]
    assert "gad_7_score" in metadata["excluded_leakage_features"]["anxiety_risk"]
    assert "pss_10_score" in metadata["excluded_leakage_features"]["stress_risk"]


def test_training_feature_selection_excludes_leakage_columns() -> None:
    from ml.scripts.train_mhp_catboost import resolve_feature_columns

    columns = [
        "age",
        "gender",
        "phq_9_score",
        "gad_7_score",
        "pss_10_score",
        "depression_risk",
        "anxiety_risk",
        "stress_risk",
        "mental_risk",
    ]
    metadata = {
        "excluded_leakage_features": {
            "depression_risk": ["phq_9_score"],
            "anxiety_risk": ["gad_7_score"],
            "stress_risk": ["pss_10_score"],
            "mental_risk": ["phq_9_score", "gad_7_score", "pss_10_score"],
        }
    }

    features = resolve_feature_columns(columns, "mental_risk", metadata)

    assert features == ["age", "gender"]


def test_prepare_mhp_dataset_prefers_total_value_columns_over_last_items(tmp_path: Path) -> None:
    from ml.scripts.prepare_mhp_dataset import prepare_dataset

    raw_path = tmp_path / "mhp_dataset.csv"
    processed_path = tmp_path / "mhp_model_dataset.csv"
    metadata_path = tmp_path / "mhp_model_metadata.json"
    pd.DataFrame(
        [
            {
                "PHQ9": 1,
                "Depression Value": 18,
                "GAD7": 1,
                "Anxiety Value": 14,
                "PSS10": 1,
                "Stress Value": 28,
            },
            {
                "PHQ9": 3,
                "Depression Value": 4,
                "GAD7": 3,
                "Anxiety Value": 4,
                "PSS10": 3,
                "Stress Value": 8,
            },
        ]
    ).to_csv(raw_path, index=False)

    metadata = prepare_dataset(raw_path, processed_path, metadata_path)
    processed = pd.read_csv(processed_path)

    assert processed["depression_risk"].tolist() == [1, 0]
    assert processed["anxiety_risk"].tolist() == [1, 0]
    assert processed["stress_risk"].tolist() == [1, 0]
    assert metadata["detected_scale_columns"]["depression_risk"]["score_column"] == "depression_value"
    assert metadata["detected_scale_columns"]["anxiety_risk"]["score_column"] == "anxiety_value"
    assert metadata["detected_scale_columns"]["stress_risk"]["score_column"] == "stress_value"


def test_mhp_prediction_uses_schema_without_target_leakage() -> None:
    from ml.scripts.predict_mhp_catboost import predict

    artifacts_dir = ROOT / "ml" / "artifacts"
    schema_path = artifacts_dir / "mhp_feature_schema_mental_risk.json"
    model_path = artifacts_dir / "mhp_catboost_mental_risk.cbm"
    if not schema_path.exists() or not model_path.exists():
        return

    payload = {
        "age": "18-22",
        "gender": "Female",
        "university": "Independent University, Bangladesh (IUB)",
        "department": "Engineering - CS / CSE / CSC / Similar to CS",
        "academic_year": "Second Year or Equivalent",
        "current_cgpa": "3.00 - 3.39",
        "waiver_or_scholarship": "No",
        "phq1": 3,
        "gad1": 3,
        "pss1": 3,
        "depression_risk": 1,
    }

    result = predict("mental_risk", payload, artifacts_dir)

    assert result["modelName"] == "MHP-CatBoost-Mental-Risk"
    assert result["screeningName"] == "心理健康风险筛查"
    assert result["resultLevel"] in {"LOW", "MEDIUM", "HIGH"}
    assert "建议进一步咨询专业人员" in result["analysis"] or result["resultLevel"] != "HIGH"
    serialized = json.dumps(result, ensure_ascii=False)
    assert "确诊抑郁" not in serialized
    assert "确诊焦虑" not in serialized
    assert "患有心理疾病" not in serialized
