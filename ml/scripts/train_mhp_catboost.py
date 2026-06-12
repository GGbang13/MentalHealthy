from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Sequence

import pandas as pd
from catboost import CatBoostClassifier, Pool
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = ROOT / "ml" / "data" / "mhp_university_students" / "processed" / "mhp_model_dataset.csv"
DEFAULT_METADATA_PATH = ROOT / "ml" / "data" / "mhp_university_students" / "processed" / "mhp_model_metadata.json"
DEFAULT_OUTPUT_DIR = ROOT / "ml" / "artifacts"
TARGET_COLUMNS = ["depression_risk", "anxiety_risk", "stress_risk", "mental_risk"]


def load_metadata(path: Path | None) -> dict:
    if path is None or not path.exists():
        return {"excluded_leakage_features": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_feature_columns(columns: Sequence[str], target: str, metadata: dict) -> list[str]:
    if target not in TARGET_COLUMNS:
        raise ValueError(f"Unsupported target: {target}")
    leakage = set(metadata.get("excluded_leakage_features", {}).get(target, []))
    excluded = set(TARGET_COLUMNS) | leakage
    return [column for column in columns if column not in excluded]


def resolve_categorical_features(frame: pd.DataFrame, feature_columns: Sequence[str]) -> list[str]:
    categorical: list[str] = []
    for column in feature_columns:
        if pd.api.types.is_object_dtype(frame[column]) or isinstance(frame[column].dtype, pd.CategoricalDtype):
            categorical.append(column)
    return categorical


def prepare_features(frame: pd.DataFrame, feature_columns: Sequence[str], categorical_features: Sequence[str]) -> pd.DataFrame:
    features = frame.loc[:, feature_columns].copy()
    for column in feature_columns:
        if column in categorical_features:
            features[column] = features[column].fillna("__missing__").astype(str)
        else:
            features[column] = pd.to_numeric(features[column], errors="coerce")
            if features[column].isna().any():
                features[column] = features[column].fillna(features[column].median())
    return features


def build_model(random_state: int) -> CatBoostClassifier:
    return CatBoostClassifier(
        loss_function="Logloss",
        eval_metric="AUC",
        iterations=500,
        learning_rate=0.05,
        depth=6,
        random_seed=random_state,
        auto_class_weights="Balanced",
        verbose=False,
    )


def resolve_split(labels: pd.Series, requested_test_size: float, random_state: int) -> dict | None:
    class_count = int(labels.nunique())
    sample_count = int(labels.shape[0])
    if class_count < 2:
        return None
    minimum_test_size = max(class_count, math.ceil(sample_count * requested_test_size))
    if sample_count <= class_count * 2 or minimum_test_size >= sample_count:
        return None
    return {"test_size": minimum_test_size, "random_state": random_state, "stratify": labels}


def evaluate(y_true: pd.Series, predictions: Sequence[int], probabilities: Sequence[float]) -> dict:
    unique_labels = int(pd.Series(y_true).nunique())
    return {
        "accuracy": round(float(accuracy_score(y_true, predictions)), 4),
        "precision": round(float(precision_score(y_true, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, predictions, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, probabilities)), 4) if unique_labels > 1 else None,
        "confusion_matrix": confusion_matrix(y_true, predictions).tolist(),
    }


def cross_validation_metrics(
    model: CatBoostClassifier,
    features: pd.DataFrame,
    labels: pd.Series,
    categorical_features: Sequence[str],
    random_state: int,
) -> dict:
    minimum_class_count = int(labels.value_counts().min()) if labels.nunique() > 1 else 0
    folds = min(5, minimum_class_count)
    if folds < 2:
        return {"folds": 0, "reason": "Not enough samples per class for stratified cross validation."}

    scoring = {
        "accuracy": "accuracy",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
        "roc_auc": "roc_auc",
    }
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    fit_params = {"cat_features": list(categorical_features)} if categorical_features else None
    cross_validate_kwargs = {"params": fit_params} if fit_params else {}
    scores = cross_validate(
        model,
        features,
        labels,
        cv=cv,
        scoring=scoring,
        error_score="raise",
        **cross_validate_kwargs,
    )
    return {
        "folds": folds,
        **{
            metric.replace("test_", ""): {
                "mean": round(float(values.mean()), 4),
                "std": round(float(values.std()), 4),
            }
            for metric, values in scores.items()
            if metric.startswith("test_")
        },
    }


def train(args: argparse.Namespace) -> dict:
    frame = pd.read_csv(args.data)
    metadata = load_metadata(args.metadata)
    if args.target not in frame.columns:
        raise ValueError(f"Target column not found in dataset: {args.target}")

    feature_columns = resolve_feature_columns(list(frame.columns), args.target, metadata)
    if not feature_columns:
        raise ValueError(f"No usable feature columns remain after leakage exclusion for {args.target}.")

    categorical_features = resolve_categorical_features(frame, feature_columns)
    features = prepare_features(frame, feature_columns, categorical_features)
    labels = pd.to_numeric(frame[args.target], errors="coerce").fillna(0).astype(int)
    if labels.nunique() < 2:
        raise ValueError(f"Target {args.target} contains fewer than two classes.")

    split_kwargs = resolve_split(labels, args.test_size, args.random_state)
    if split_kwargs is None:
        x_train = features
        x_test = features
        y_train = labels
        y_test = labels
    else:
        x_train, x_test, y_train, y_test = train_test_split(features, labels, **split_kwargs)

    train_pool = Pool(x_train, label=y_train, cat_features=list(categorical_features))
    test_pool = Pool(x_test, label=y_test, cat_features=list(categorical_features))
    model = build_model(args.random_state)
    model.fit(train_pool, eval_set=test_pool, use_best_model=True)

    probabilities = model.predict_proba(x_test)[:, 1].tolist()
    predictions = model.predict(x_test).astype(int).tolist()
    metrics = evaluate(y_test, predictions, probabilities)
    metrics["cross_validation"] = cross_validation_metrics(
        build_model(args.random_state),
        features,
        labels,
        categorical_features,
        args.random_state,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.output_dir / f"mhp_catboost_{args.target}.cbm"
    schema_path = args.output_dir / f"mhp_feature_schema_{args.target}.json"
    metrics_path = args.output_dir / f"mhp_metrics_{args.target}.json"
    model.save_model(model_path)

    schema = {
        "target": args.target,
        "features": feature_columns,
        "categorical_features": categorical_features,
        "excluded_leakage_features": metadata.get("excluded_leakage_features", {}).get(args.target, []),
        "model_path": str(model_path.as_posix()),
        "screening_terms": {
            "module_name": "心理健康风险筛查",
            "high_risk_label": "较高风险",
            "recommendation": "建议进一步咨询专业人员",
        },
    }
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

    metrics_payload = {
        "target": args.target,
        "rows": int(frame.shape[0]),
        "feature_count": len(feature_columns),
        "categorical_features": categorical_features,
        **metrics,
    }
    metrics_path.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "model_file": str(model_path.as_posix()),
        "schema_file": str(schema_path.as_posix()),
        "metrics_file": str(metrics_path.as_posix()),
        "metrics": metrics_payload,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train CatBoost for MHP university student risk screening.")
    parser.add_argument("--target", required=True, choices=TARGET_COLUMNS)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    print(json.dumps(train(parse_args()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
