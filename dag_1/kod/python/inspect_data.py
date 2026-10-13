#!/usr/bin/env python3
"""Första inspektion av AI4I 2020 för dag 1."""

from pathlib import Path

import pandas as pd


CODE_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = CODE_DIR / "data/ai4i2020.csv"


def main() -> None:
    data = pd.read_csv(DATA_FILE, encoding="utf-8-sig")

    print("Första fem raderna:")
    print(data.head())
    print("\nForm (rader, kolumner):", data.shape)
    print("\nDatatyper:")
    print(data.dtypes)
    print("\nSaknade värden:")
    print(data.isna().sum())
    print("\nDubbletter:", data.duplicated().sum())
    print("\nMaskinfel:", int(data["Machine failure"].sum()))
    print("Andel maskinfel:", f'{data["Machine failure"].mean():.2%}')


if __name__ == "__main__":
    main()
