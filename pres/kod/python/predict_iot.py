#!/usr/bin/env python3
"""Ladda en sparad modell och förutsäg maskinfel från egna mätvärden."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import joblib
import pandas as pd


CODE_DIR = Path(__file__).resolve().parents[1]


def measurement(value: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("Ange ett tal, med punkt som decimaltecken.") from None
    if not math.isfinite(number) or number < 0:
        raise argparse.ArgumentTypeError("Mätvärdet måste vara ett ändligt tal som är minst 0.")
    return number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-wear", type=measurement, required=True, help="Verktygsslitage i minuter.")
    parser.add_argument("--torque", type=measurement, required=True, help="Vridmoment i Nm.")
    parser.add_argument("--model", type=Path, default=CODE_DIR / "output/model.joblib")
    args = parser.parse_args()

    if not args.model.is_file():
        parser.error(f"Modellfilen saknas: {args.model}. Kör train_iot.py först.")

    # Här sker ingen träning. Läs in modellen och använd dess kolumnordning.
    model = joblib.load(args.model)
    observation = pd.DataFrame([{
        "tool_wear_min": args.tool_wear,
        "torque_nm": args.torque,
    }])[list(model.feature_names_in_)]
    prediction = int(model.predict(observation)[0])
    label = "maskinfel" if prediction == 1 else "normal drift"
    print(f"Förutsägelse: {label}")


if __name__ == "__main__":
    main()
