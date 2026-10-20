#!/usr/bin/env python3
"""Klassificera maskinfel i AI4I och jämför med en enkel baslinje."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_FEATURES = [
    "air_temperature_k",
    "process_temperature_k",
    "rotational_speed_rpm",
    "torque_nm",
    "tool_wear_min",
    "power_w",
    "temperature_difference_k",
]
CATEGORICAL_FEATURES = ["type"]
CODE_DIR = Path(__file__).resolve().parents[1]


def metrics(y_true: pd.Series, prediction) -> dict[str, float | list[list[int]]]:
    return {
        "accuracy": accuracy_score(y_true, prediction),
        "precision": precision_score(y_true, prediction, zero_division=0),
        "recall": recall_score(y_true, prediction, zero_division=0),
        "f1": f1_score(y_true, prediction, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, prediction).tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=CODE_DIR / "output/model_metrics.json")
    args = parser.parse_args()

    data = pd.read_csv(args.input)
    x = data[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = data["machine_failure"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    preprocess = ColumnTransformer([
        ("numeric", StandardScaler(), NUMERIC_FEATURES),
        ("type", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    model = Pipeline([
        ("preprocess", preprocess),
        ("classifier", LogisticRegression(max_iter=2_000, class_weight="balanced")),
    ])
    baseline = DummyClassifier(strategy="most_frequent")

    model.fit(x_train, y_train)
    baseline.fit(x_train, y_train)

    # Kontrollera och förtydliga vilka typer vi förväntar oss.
    assert isinstance(x_train, pd.DataFrame)
    assert isinstance(x_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)

    # Larma om både slitaget och vridmomentet är höga.
    rule_predictions = (
        (x_test["tool_wear_min"] >= 150)
        & (x_test["torque_nm"].between(40, 80))
    ).astype(int)

    result = {
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "test_failure_rate": float(y_test.mean()),
        "model": metrics(y_test, model.predict(x_test)),
        "baseline": metrics(y_test, baseline.predict(x_test)),
        "rule_pred": metrics(y_test, rule_predictions),
        "note": "Feltypskolumnerna TWF/HDF/PWF/OSF/RNF används inte eftersom de läcker målet.",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
