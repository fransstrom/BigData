#!/usr/bin/env python3
"""Träna ett beslutsträd för maskinfel och spara det för senare användning."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier


CODE_DIR = Path(__file__).resolve().parents[1]
FEATURES = ["tool_wear_min", "torque_nm"]
MIN_RECALL = 0.80


def rank_candidates(cv_results: dict) -> pd.DataFrame:
    """Prioritera recall-kravet och därefter precision; använd bara CV-resultat."""
    results = pd.DataFrame(cv_results)
    results["meets_recall_target"] = results["mean_test_recall"] >= MIN_RECALL
    if results["meets_recall_target"].any():
        order = ["meets_recall_target", "mean_test_precision", "mean_test_recall"]
    else:
        # Om ingen når målet, välj högst recall och redovisa att målet missades.
        order = ["mean_test_recall", "mean_test_precision"]
    return results.sort_values(order, ascending=False, kind="stable")


def select_candidate(cv_results: dict) -> int:
    return int(rank_candidates(cv_results).index[0])


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
        "input", type=Path, nargs="?", default=CODE_DIR / "output/ai4i_clean.csv",
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

    # Prova 36 kombinationer på samma fem uppdelningar av enbart träningsdatan.
    parameters = {
        "max_depth": [3, 5, 7],
        "min_samples_leaf": [5, 10, 20],
        "class_weight": [None, {0: 1, 1: 5}, {0: 1, 1: 10}, "balanced"],
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    search = GridSearchCV(
        estimator=DecisionTreeClassifier(random_state=42),
        param_grid=parameters,
        scoring={
            "precision": make_scorer(precision_score, zero_division=0),
            "recall": make_scorer(recall_score, zero_division=0),
            "f1": make_scorer(f1_score, zero_division=0),
        },
        refit=select_candidate,
        cv=cv,
        n_jobs=-1,
        error_score="raise",
    )
    print("Jämför 36 kombinationer med 5-faldig korsvalidering...", flush=True)
    search.fit(x_train, y_train)
    # Vinnaren är omtränad på hela träningsmängden. Sluttestet används först nedan.
    model = search.best_estimator_
    selected = rank_candidates(search.cv_results_).loc[search.best_index_]
    print(f"Valda inställningar: {search.best_params_}")
    print(f"Recall vid korsvalidering: {selected['mean_test_recall']:.1%}")
    print(f"Precision vid korsvalidering: {selected['mean_test_precision']:.1%}")
    if not selected["meets_recall_target"]:
        print(f"Ingen kombination nådde {MIN_RECALL:.0%} recall. Valde högst recall i stället.")

    # Kontrollera och förtydliga vilka typer vi förväntar oss.
    assert isinstance(x_train, pd.DataFrame)
    assert isinstance(x_test, pd.DataFrame)
    assert isinstance(y_train, pd.Series)
    assert isinstance(y_test, pd.Series)


    # Baslinjen förutsäger alltid normal drift på samma testdata.
    baseline = DummyClassifier(strategy="constant", constant=0)
    baseline.fit(x_train, y_train)
    result = {
        "features": FEATURES,
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "test_failure_rate": float(y_test.mean()),
        "search": {
            "candidates": len(search.cv_results_["params"]),
            "cv_folds": search.n_splits_,
            "selection_rule": "highest_precision_with_minimum_recall_else_highest_recall",
            "minimum_cv_recall": MIN_RECALL,
            "recall_target_met": bool(selected["meets_recall_target"]),
            "best_params": search.best_params_,
            "best_cv_precision": float(selected["mean_test_precision"]),
            "best_cv_recall": float(selected["mean_test_recall"]),
            "best_cv_f1": float(selected["mean_test_f1"]),
        },
        "model": metrics(y_test, model.predict(x_test)),
        "baseline": metrics(y_test, baseline.predict(x_test)),
    }

    # Varje körning tränar på nytt. Prediktionsskriptet behöver bara modellfilen.
    args.output.mkdir(parents=True, exist_ok=True)
    # mean_test_* avser valideringsdelarna inom träningsdatan, inte sluttestet.
    results = rank_candidates(search.cv_results_)
    results["selection_rank"] = range(1, len(results) + 1)
    results["selected"] = results.index == search.best_index_
    results["param_class_weight"] = results["params"].map(lambda params: str(params["class_weight"]))
    columns = [
        "selection_rank", "selected", "meets_recall_target",
        "param_max_depth", "param_min_samples_leaf", "param_class_weight",
        "mean_test_precision", "mean_test_recall", "mean_test_f1", "std_test_recall", "std_test_f1",
    ]
    results[columns].to_csv(args.output / "model_search.csv", index=False)
    model_path = args.output / "model.joblib"
    joblib.dump(model, model_path)
    report = json.dumps(result, indent=2) + "\n"
    (args.output / "model_metrics.json").write_text(report, encoding="utf-8")
    print(report, end="")
    print(f"Modellen sparad: {model_path}")


if __name__ == "__main__":
    main()
