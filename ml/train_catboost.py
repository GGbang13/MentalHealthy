from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from catboost import CatBoostClassifier, Pool
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split


@dataclass(frozen=True)
class ScaleSchema:
    code: str
    features: list[str]
    target: str = "label"


SCHEMAS = {
    "PHQ9": ScaleSchema(
        code="PHQ9",
        features=[
            "moodLow",
            "anhedonia",
            "sleepProblem",
            "fatigue",
            "concentrationDifficulty",
            "selfWorthLow",
            "socialWithdrawal",
            "stressLoad",
            "exerciseFrequency",
            "familySupport",
        ],
    ),
    "GAD7": ScaleSchema(
        code="GAD7",
        features=[
            "nervousness",
            "uncontrollableWorry",
            "irritability",
            "restlessness",
            "muscleTension",
            "sleepProblem",
            "workPressure",
            "familyConflict",
            "socialIsolation",
            "relaxationAbility",
        ],
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a CatBoost model for mental health risk prediction.")
    parser.add_argument("--scale", required=True, choices=sorted(SCHEMAS.keys()), help="Supported scales: PHQ9 or GAD7.")
    parser.add_argument("--data", required=True, type=Path, help="CSV file containing questionnaire variables and label.")
    parser.add_argument(
        "--output-dir",
        default=Path("ml/artifacts"),
        type=Path,
        help="Directory used to save model and feature importance files.",
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Fraction of the dataset used for validation.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed.")
    return parser.parse_args()


def validate_columns(frame: pd.DataFrame, schema: ScaleSchema) -> None:
    required_columns = schema.features + [schema.target]
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        missing_joined = ", ".join(missing_columns)
        raise ValueError(
            f"Dataset is missing required columns for {schema.code}: {missing_joined}. "
            f"Expected columns: {', '.join(required_columns)}"
        )


def build_model() -> CatBoostClassifier:
    return CatBoostClassifier(
        loss_function="Logloss",
        eval_metric="AUC",
        iterations=400,
        learning_rate=0.05,
        depth=6,
        random_seed=42,
        verbose=False,
    )


def resolve_split(labels: pd.Series, requested_test_size: float, random_state: int):
    class_count = int(labels.nunique())
    sample_count = int(labels.shape[0])
    minimum_test_size = max(class_count, math.ceil(sample_count * requested_test_size))

    if sample_count <= class_count * 2 or minimum_test_size >= sample_count:
        return None

    return {
        "test_size": minimum_test_size,
        "random_state": random_state,
        "stratify": labels,
    }


def save_feature_importance(
    model: CatBoostClassifier,
    valid_pool: Pool,
    schema: ScaleSchema,
    output_dir: Path,
) -> pd.DataFrame:
    importance = model.get_feature_importance(valid_pool, type="FeatureImportance")
    importance_frame = pd.DataFrame(
        {
            "feature": schema.features,
            "importance": importance,
        }
    ).sort_values("importance", ascending=False)

    importance_frame.to_csv(output_dir / f"{schema.code.lower()}_feature_importance.csv", index=False, encoding="utf-8-sig")
    (output_dir / f"{schema.code.lower()}_feature_importance.json").write_text(
        importance_frame.to_json(orient="records", force_ascii=False, indent=2),
        encoding="utf-8",
    )
    return importance_frame


def save_metrics(
    y_true: pd.Series,
    y_pred: list[int],
    y_prob: list[float],
    schema: ScaleSchema,
    output_dir: Path,
) -> dict:
    unique_labels = pd.Series(y_true).nunique()
    metrics = {
        "scale": schema.code,
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_prob)), 4) if unique_labels > 1 else None,
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
    }
    (output_dir / f"{schema.code.lower()}_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return metrics


def main() -> None:
    args = parse_args()
    schema = SCHEMAS[args.scale]

    frame = pd.read_csv(args.data)
    validate_columns(frame, schema)

    features = frame[schema.features]
    labels = frame[schema.target]

    split_kwargs = resolve_split(labels, args.test_size, args.random_state)
    if split_kwargs is None:
        x_train = features
        y_train = labels
        x_valid = features
        y_valid = labels
    else:
        x_train, x_valid, y_train, y_valid = train_test_split(features, labels, **split_kwargs)

    train_pool = Pool(x_train, label=y_train)
    valid_pool = Pool(x_valid, label=y_valid)

    model = build_model()
    model.fit(train_pool, eval_set=valid_pool, use_best_model=True)

    output_dir = args.output_dir / schema.code.lower()
    output_dir.mkdir(parents=True, exist_ok=True)

    model.save_model(output_dir / f"{schema.code.lower()}_catboost_model.cbm")

    probabilities = model.predict_proba(x_valid)[:, 1]
    predictions = model.predict(x_valid).astype(int).tolist()

    metrics = save_metrics(y_valid, predictions, probabilities.tolist(), schema, output_dir)
    importance = save_feature_importance(model, valid_pool, schema, output_dir)

    summary = {
        "scale": schema.code,
        "rows": int(frame.shape[0]),
        "feature_count": len(schema.features),
        "top_features": importance.head(5).to_dict(orient="records"),
        "metrics_file": str((output_dir / f"{schema.code.lower()}_metrics.json").as_posix()),
        "model_file": str((output_dir / f"{schema.code.lower()}_catboost_model.cbm").as_posix()),
    }
    (output_dir / "training_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({"summary": summary, "metrics": metrics}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
