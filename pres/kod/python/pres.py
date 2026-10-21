#!/usr/bin/env python3
"""Inspektera, behandla och visualisera AI4I 2020-datasetet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

# Hitta kodmappen utifrån skriptets plats och lägg Matplotlibs cache där.
CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(CODE_DIR / ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd

# Ge CSV-filens kolumner kortare namn som är enklare att använda i koden.
RENAME = {
    "UDI": "udi",
    "Product ID": "product_id",
    "Type": "type",
    "Air temperature [K]": "air_temperature_k",
    "Process temperature [K]": "process_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "machine_failure",
}

def main() -> None:
    # Läs in filnamnet från terminalen. --output kan ändra var resultaten sparas.
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=CODE_DIR / "data/ai4i2020.csv")
    parser.add_argument("--output", type=Path, default=CODE_DIR / "output")
    args = parser.parse_args()

    # Läs CSV-filen till en tabell. utf-8-sig hanterar filens eventuella BOM-markör.
    data = pd.read_csv(args.input, encoding="utf-8-sig").rename(columns=RENAME)
    original_rows = len(data)
    duplicate_rows = int(data.duplicated().sum())

    # Ta bort helt identiska rader; samma mätvärden med olika ID räknas inte som dubbletter.
    data = data.drop_duplicates().copy()

    # Varje kontroll ger True/False per rad. & kräver att alla villkor är uppfyllda.
    # Temperaturgränserna är rimlighetskontroller från kursmallen.
    valid = (
        data["air_temperature_k"].between(250, 350)
        & data["process_temperature_k"].between(250, 400)
        & data["rotational_speed_rpm"].gt(0)
        & data["torque_nm"].ge(0)
        & data["tool_wear_min"].ge(0)
        & data["machine_failure"].isin([0, 1])
    )


    # Behåll bara godkända rader i en separat tabell för analysen.
    clean = data.loc[valid].copy()


    # Skapa två True/False-kolumner för lågt/högt slitage och vridmoment.
    # 180 min och 60 Nm är valda analysgränser, inte fastställda gränser för maskinfel.
    clean["high_tool_wear"] = clean["tool_wear_min"] >= 180
    clean["high_torque"] = clean["torque_nm"] >= 60

    # Sammanfatta de fyra kombinationerna av lågt/högt slitage och vridmoment.
    # Maskinfel är 0 eller 1: summan ger antal fel och medelvärdet ger felandelen.
    summary = clean.groupby(["high_torque", "high_tool_wear"]).agg(
        observations=("machine_failure", "size"),
        failures=("machine_failure", "sum"),
        failure_rate=("machine_failure", "mean"),
        mean_torque_nm=("torque_nm", "mean"),
        mean_tool_wear_min=("tool_wear_min", "mean")
    )

    # Omvandla andelen (0–1) till procent (0–100).
    summary["failure_rate_pct"] = summary["failure_rate"]*100
    print(summary)

    # Spara även en separat tabell med enbart observationer där maskinfel inträffat.
    failures = clean[clean["machine_failure"] == 1].copy()

    # Dokumentera datakontrollerna. Saknade värden räknas före filtrering,
    # efter att dubbletter tagits bort. ~valid markerar de underkända raderna.
    quality = {
        "source_rows": original_rows,
        "duplicate_rows": duplicate_rows,
        "missing_values": int(data.isna().sum().sum()),
        "invalid_rows": int((~valid).sum()),
        "clean_rows": len(clean),
        "machine_failures": int(clean["machine_failure"].sum()),
        "failure_rate": float(clean["machine_failure"].mean()),
    }

    # Skapa resultatmappen och spara tabeller som kan användas i presentationen.
    args.output.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output / "pres_ai4i_clean.csv", index=False)
    summary.to_csv(args.output / "pres_summary_machine_failure_by_torque_and_tool_wear.csv")
    failures.to_csv(args.output / "pres_machine_failures.csv", index=False)

    # JSON sparar kvalitetsrapportens namn och värden i ett läsbart format.
    (args.output / "pres_quality_report.json").write_text(
        json.dumps(quality, indent=2) + "\n", encoding="utf-8"
    )


    # Skapa ett punktdiagram: varje punkt är en observation.
    fig, ax = plt.subplots(figsize=(8, 5))
    normal = clean[clean["machine_failure"] == 0]
    failed = clean[clean["machine_failure"] == 1]
    # Normal drift ritas först med små, genomskinliga punkter (s = storlek, alpha = opacitet).
    ax.scatter(
        normal["tool_wear_min"], normal["torque_nm"],
        s=8, alpha=0.2, label="Normal drift"
    )
    # Rita maskinfelen ovanpå med större, tydligare punkter.
    ax.scatter(
        failed["tool_wear_min"], failed["torque_nm"],
        s=18, alpha=0.75, label="Maskinfel"
    )
    # Ange vad axlarna visar och vilka enheter som används.
    ax.set_title("Verktygsslitage och vridmoment")
    ax.set_xlabel("Verktygsslitage (min)")
    ax.set_ylabel("Vridmoment (Nm)")
    ax.legend()
    ax.grid(alpha=0.2)

    # Anpassa marginalerna och spara diagrammet som en PNG-bild.
    fig.tight_layout()
    fig.savefig(args.output / "pres_ai4i_overview.png", dpi=160)

    print(json.dumps(quality, indent=2))


# Kör analysen när filen startas direkt, men inte när den importeras.
if __name__ == "__main__":
    main()
