#!/usr/bin/env python3
"""Inspektera, behandla och visualisera AI4I 2020-datasetet."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(CODE_DIR / ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd


RENAME = {
    "Torque [Nm]": "torque_nm",
    "Tool wear [min]": "tool_wear_min",
    "Machine failure": "machine_failure",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=CODE_DIR / "output")
    args = parser.parse_args()

    data = pd.read_csv(args.input, encoding="utf-8-sig").rename(columns=RENAME)
    original_rows = len(data)
    duplicate_rows = int(data.duplicated().sum())

    # Identifierare behövs för spårbarhet men ska inte tolkas som mätvärden.
    data = data.drop_duplicates().copy()

    # Fysikaliska storheter och tydliga rimlighetskontroller.
    valid = (
        data["torque_nm"].ge(0)
        & data["tool_wear_min"].ge(0)
        & data["machine_failure"].isin([0, 1])
    )

    clean = data.loc[valid].copy()


    summary = clean.groupby("machine_failure").agg(
        failures=("machine_failure", "sum"),
        failure_rate=("machine_failure", "mean"),
        mean_torque_nm=("torque_nm", "mean"),
        mean_tool_wear_min=("tool_wear_min", "mean")
    )

    failures = clean[clean["machine_failure"] == 1].copy()

    quality = {
        "source_rows": original_rows,
        "duplicate_rows": duplicate_rows,
        "missing_values": int(data.isna().sum().sum()),
        "invalid_rows": int((~valid).sum()),
        "clean_rows": len(clean),
        "machine_failures": int(clean["machine_failure"].sum()),
        "failure_rate": float(clean["machine_failure"].mean()),
    }

    args.output.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output / "ai4i_clean.csv", index=False)
    summary.to_csv(args.output / "summary_by_type.csv")
    failures.to_csv(args.output / "machine_failures.csv", index=False)
    (args.output / "quality_report.json").write_text(
        json.dumps(quality, indent=2) + "\n", encoding="utf-8"
    )


    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    normal = clean[clean["machine_failure"] == 0]
    failed = clean[clean["machine_failure"] == 1]
    axes[0].scatter(
        normal["tool_wear_min"], normal["torque_nm"],
        s=8, alpha=0.2, label="Normal drift"
    )
    axes[0].scatter(
        failed["tool_wear_min"], failed["torque_nm"],
        s=18, alpha=0.75, label="Maskinfel"
    )
    # axes[0].set_title("Varvtal och vridmoment")
    # axes[0].set_xlabel("Rotationshastighet (rpm)")
    # axes[0].set_ylabel("Vridmoment (Nm)")
    # axes[0].legend()
    # axes[0].grid(alpha=0.2)
    #
    # rates = clean.groupby("machine_failure")["tool_wear_min"].sort_index() * 100
    # axes[1].bar(rates.index, rates.values, color="#4c78a8")
    # axes[1].set_title("Andel maskinfel per produkttyp")
    # axes[1].set_xlabel("Produkttyp")
    # axes[1].set_ylabel("Maskinfel (%)")
    # axes[1].grid(axis="y", alpha=0.2)
    #
    fig.tight_layout()
    fig.savefig(args.output / "ai4i_overview.png", dpi=160)

    print(json.dumps(quality, indent=2))


if __name__ == "__main__":
    main()
