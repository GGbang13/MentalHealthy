from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_PATH = ROOT / "ml" / "data" / "mhp_university_students" / "raw" / "mhp_dataset.csv"
DEFAULT_PROCESSED_PATH = (
    ROOT / "ml" / "data" / "mhp_university_students" / "processed" / "mhp_model_dataset.csv"
)
DEFAULT_METADATA_PATH = (
    ROOT / "ml" / "data" / "mhp_university_students" / "processed" / "mhp_model_metadata.json"
)

TARGET_COLUMNS = ["depression_risk", "anxiety_risk", "stress_risk", "mental_risk"]
DIRECT_RISK_COLUMNS = {
    "depression_risk": ["depression_risk", "depressed_risk", "depression_binary"],
    "anxiety_risk": ["anxiety_risk", "anxious_risk", "anxiety_binary"],
    "stress_risk": ["stress_risk", "stress_binary"],
}
SCORE_PATTERNS = {
    "depression_risk": [
        r"^depression_(value|score|total|sum)$",
        r"phq_?9.*(total|score|sum)?$",
        r"depression.*(score|total|sum)$",
        r"depression$",
    ],
    "anxiety_risk": [
        r"^anxiety_(value|score|total|sum)$",
        r"gad_?7.*(total|score|sum)?$",
        r"anxiety.*(score|total|sum)$",
        r"anxiety$",
    ],
    "stress_risk": [
        r"^stress_(value|score|total|sum)$",
        r"pss_?10.*(total|score|sum)?$",
        r"stress.*(score|total|sum)$",
        r"stress$",
    ],
}
ITEM_PATTERNS = {
    "depression_risk": [r"^phq_?9?_?q?\d+$", r"^phq\d+$", r"^depression_?q?\d+$"],
    "anxiety_risk": [r"^gad_?7?_?q?\d+$", r"^gad\d+$", r"^anxiety_?q?\d+$"],
    "stress_risk": [r"^pss_?10?_?q?\d+$", r"^pss\d+$", r"^stress_?q?\d+$"],
}
RISK_THRESHOLDS = {
    "depression_risk": 10.0,
    "anxiety_risk": 10.0,
    "stress_risk": 20.0,
}
TARGET_KEYWORDS = {
    "depression_risk": ["phq", "depression", "depress"],
    "anxiety_risk": ["gad", "anxiety", "anxious"],
    "stress_risk": ["pss", "stress"],
}


def to_snake_case(value: str) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "unnamed"


def deduplicate_columns(columns: Iterable[str]) -> list[str]:
    seen: dict[str, int] = {}
    result: list[str] = []
    for column in columns:
        base = to_snake_case(column)
        count = seen.get(base, 0)
        seen[base] = count + 1
        result.append(base if count == 0 else f"{base}_{count + 1}")
    return result


def read_raw_csv(raw_path: Path) -> pd.DataFrame:
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {raw_path}. Place the MHP CSV at this path before preprocessing."
        )
    return pd.read_csv(raw_path)


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    normalized = frame.copy()
    normalized.columns = deduplicate_columns(normalized.columns)
    return normalized


def matched_columns(columns: Iterable[str], patterns: Iterable[str]) -> list[str]:
    compiled = [re.compile(pattern) for pattern in patterns]
    return [column for column in columns if any(pattern.search(column) for pattern in compiled)]


def coerce_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def parse_binary_risk(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return coerce_numeric(series).fillna(0).gt(0).astype(int)
    normalized = series.astype(str).str.strip().str.lower()
    positive_values = {"1", "yes", "y", "true", "risk", "high", "moderate", "severe", "present"}
    return normalized.isin(positive_values).astype(int)


def derive_risk_from_score(frame: pd.DataFrame, target: str, source_column: str) -> pd.Series:
    scores = coerce_numeric(frame[source_column])
    threshold = RISK_THRESHOLDS[target]
    return scores.ge(threshold).fillna(False).astype(int)


def derive_risk_from_items(frame: pd.DataFrame, target: str, item_columns: list[str]) -> pd.Series:
    scores = frame[item_columns].apply(coerce_numeric).sum(axis=1, min_count=1)
    threshold = RISK_THRESHOLDS[target]
    return scores.ge(threshold).fillna(False).astype(int)


def find_score_column(frame: pd.DataFrame, target: str) -> str | None:
    for pattern in SCORE_PATTERNS[target]:
        candidates = matched_columns(frame.columns, [pattern])
        for column in candidates:
            if column not in TARGET_COLUMNS and pd.api.types.is_numeric_dtype(coerce_numeric(frame[column])):
                return column
    return None


def find_item_columns(frame: pd.DataFrame, target: str) -> list[str]:
    candidates = matched_columns(frame.columns, ITEM_PATTERNS[target])
    return [column for column in candidates if pd.api.types.is_numeric_dtype(coerce_numeric(frame[column]))]


def find_direct_risk_column(frame: pd.DataFrame, target: str) -> str | None:
    for column in DIRECT_RISK_COLUMNS[target]:
        if column in frame.columns:
            return column
    return None


def detect_scale_columns(frame: pd.DataFrame) -> dict[str, dict[str, list[str] | str | None]]:
    detected: dict[str, dict[str, list[str] | str | None]] = {}
    for target in ["depression_risk", "anxiety_risk", "stress_risk"]:
        detected[target] = {
            "direct_risk_column": find_direct_risk_column(frame, target),
            "score_column": find_score_column(frame, target),
            "item_columns": find_item_columns(frame, target),
        }
    return detected


def build_risk_targets(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict[str, list[str] | str | None]]]:
    processed = frame.copy()
    detected = detect_scale_columns(processed)
    for target, source in detected.items():
        direct_column = source["direct_risk_column"]
        score_column = source["score_column"]
        item_columns = source["item_columns"]
        if isinstance(direct_column, str):
            processed[target] = parse_binary_risk(processed[direct_column])
        elif isinstance(score_column, str):
            processed[target] = derive_risk_from_score(processed, target, score_column)
        elif isinstance(item_columns, list) and item_columns:
            processed[target] = derive_risk_from_items(processed, target, item_columns)
        else:
            processed[target] = 0

    processed["mental_risk"] = processed[["depression_risk", "anxiety_risk", "stress_risk"]].max(axis=1)
    return processed, detected


def build_missing_value_report(frame: pd.DataFrame) -> dict[str, int]:
    missing = frame.isna().sum()
    return {column: int(count) for column, count in missing.items() if int(count) > 0}


def build_abnormal_value_report(frame: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    report: dict[str, dict[str, float | int]] = {}
    for column in frame.columns:
        numeric = coerce_numeric(frame[column])
        if numeric.notna().sum() == 0:
            continue
        minimum = float(numeric.min())
        maximum = float(numeric.max())
        negative_count = int(numeric.lt(0).sum())
        suspicious_count = int(numeric.gt(100).sum())
        if negative_count or suspicious_count:
            report[column] = {
                "min": minimum,
                "max": maximum,
                "negative_count": negative_count,
                "above_100_count": suspicious_count,
            }
    return report


def build_excluded_leakage_features(
    frame: pd.DataFrame,
    detected: dict[str, dict[str, list[str] | str | None]],
) -> dict[str, list[str]]:
    exclusions: dict[str, list[str]] = {}
    for target in ["depression_risk", "anxiety_risk", "stress_risk"]:
        source = detected[target]
        target_exclusions: set[str] = set()
        for key in ["direct_risk_column", "score_column"]:
            value = source.get(key)
            if isinstance(value, str):
                target_exclusions.add(value)
        item_columns = source.get("item_columns")
        if isinstance(item_columns, list):
            target_exclusions.update(item_columns)
        for column in frame.columns:
            if any(keyword in column for keyword in TARGET_KEYWORDS[target]):
                target_exclusions.add(column)
        target_exclusions.discard(target)
        exclusions[target] = sorted(target_exclusions)

    exclusions["mental_risk"] = sorted(
        set(exclusions["depression_risk"])
        | set(exclusions["anxiety_risk"])
        | set(exclusions["stress_risk"])
        | {"depression_risk", "anxiety_risk", "stress_risk"}
    )
    return exclusions


def prepare_dataset(raw_path: Path, processed_path: Path, metadata_path: Path | None = None) -> dict:
    raw_frame = read_raw_csv(raw_path)
    normalized = normalize_columns(raw_frame)
    processed, detected = build_risk_targets(normalized)
    excluded_leakage_features = build_excluded_leakage_features(processed, detected)

    processed_path.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(processed_path, index=False, encoding="utf-8-sig")

    metadata = {
        "source_dataset": "MHP: Anxiety, Stress, Depression Dataset of University Students",
        "raw_path": str(raw_path.as_posix()),
        "processed_path": str(processed_path.as_posix()),
        "rows": int(processed.shape[0]),
        "columns": list(processed.columns),
        "detected_scale_columns": detected,
        "missing_values": build_missing_value_report(processed),
        "abnormal_values": build_abnormal_value_report(processed),
        "risk_thresholds": RISK_THRESHOLDS,
        "target_columns": TARGET_COLUMNS,
        "excluded_leakage_features": excluded_leakage_features,
        "screening_disclaimer": "This dataset is for mental health risk screening, not medical diagnosis.",
    }
    if metadata_path is not None:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare the MHP university students dataset for modeling.")
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_PROCESSED_PATH)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = prepare_dataset(args.raw, args.output, args.metadata)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
