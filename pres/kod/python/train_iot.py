#!/usr/bin/env python3
"""Träna ett beslutsträd för maskinfel och spara det för senare användning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


CODE_DIR = Path(__file__).resolve().parents[1]
FEATURES = ["tool_wear_min", "torque_nm"]


def metrics(y_true: pd.Series, prediction) -> dict[str, float | int]:
    # Rader = verkligt utfall, kolumner = förutsägelse; normal drift först.
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "accuracy": float(accuracy_score(y_true, prediction)),
        "precision": float(precision_score(y_true, prediction, zero_division=0)),
        "recall": float(recall_score(y_true, prediction, zero_division=0)),
        "f1": float(f1_score(y_true, prediction, zero_division=0 )),
        "correct_predictions": int(tn + tp),
        "correct_normal": int(tn),
        "detected_failures": int(tp),
        "missed_failures": int(fn),
        "false_alarms": int(fp),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, nargs="?", default=CODE_DIR / "output/pres_ai4i_clean.csv",
        help="Rensad CSV från pres.py.",
    )
    parser.add_argument("--output", type=Path, default=CODE_DIR / "output")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Datafilen saknas: {args.input}. Kör pres.py först.")
    data = pd.read_csv(args.input)
    required = FEATURES + ["machine_failure"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        parser.error(f"CSV-filen saknar kolumner: {', '.join(missing)}")

    # Använd bara slitage och vridmoment. Feltypskolumnerna skulle läcka svaret.
    x = data[FEATURES]
    y = data["machine_failure"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y,
    )

    # Ett litet träd är lättare att förklara. Klassvikter ger de få felen större vikt.
    model = DecisionTreeClassifier(
        max_depth=3, min_samples_leaf=10, class_weight="balanced", random_state=42,
    )
    model.fit(x_train, y_train)

    # Kontrollera och förtydliga vilka typer vi förväntar oss.
    assert isinstance(x_train, pd.DataFrame)
    assert isinstance(x_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)

    rule_predictions = (
          (x_test["tool_wear_min"] >= 180)
          | (x_test["torque_nm"] >= 60)
      ).astype(int)


    # Baslinjen förutsäger alltid normal drift på samma testdata.
    baseline = DummyClassifier(strategy="constant", constant=0)
    baseline.fit(x_train, y_train)
    result = {
        "features": FEATURES,
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "test_failure_rate": float(y_test.mean()),
        "model": metrics(y_test, model.predict(x_test)),
        "baseline": metrics(y_test, baseline.predict(x_test)),
        "rules_pred": metrics(y_test, rule_predictions)
    }

    # Varje körning tränar på nytt. Prediktionsskriptet behöver bara modellfilen.
    args.output.mkdir(parents=True, exist_ok=True)
    model_path = args.output / "model.joblib"
    joblib.dump(model, model_path)
    report = json.dumps(result, indent=2) + "\n"
    (args.output / "model_metrics.json").write_text(report, encoding="utf-8")
    print(report, end="")
    print(f"Modellen sparad: {model_path}")


if __name__ == "__main__":
    main()
