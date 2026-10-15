# Övningar dag 2

## Övning 1 – När datan växer

AI4I har 10 000 rader. Anta att samma schema används för 100 miljoner observationer.

Besvara:

1. Vilka kolumner behövs för din fråga?
2. Vilka kolumner kan läsas bort tidigt?
3. Hur skulle data kunna partitioneras?
4. Vilka sammanfattningar kan beräknas i förväg?
5. När räcker en starkare dator?
6. När kan distribuerad behandling behövas?

## Laboration – Från AI4I till visualisering

```bash
source .venv/bin/activate
python dag_2/kod/python/download_data.py
python dag_2/kod/python/analyze_iot.py \
  dag_2/kod/data/ai4i2020.csv
```

Läs därefter den behandlade filen:

```python
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("dag_2/kod/output/ai4i_clean.csv")
```

### Uppgift A – Sammanfatta per produkttyp

Skapa en tabell med antal observationer, antal maskinfel, felandel och genomsnittligt vridmoment per `type`.

```python
summary = data.groupby("type").agg(
    observations=("udi", "size"),
    failures=("machine_failure", "sum"),
    failure_rate=("machine_failure", "mean"),
    mean_torque=("torque_nm", "mean"),
)
```

### Uppgift B – Skapa features

Kontrollera hur `power_w` och `temperature_difference_k` har beräknats. Förklara vad de betyder och vilka enheter de har.

Skapa sedan en egen enkel feature, till exempel:

```python
data["high_tool_wear"] = data["tool_wear_min"] > 180
```

### Uppgift C – Visualisera

Skapa minst två diagram:

1. felandel per produkttyp,
2. punktdiagram med rotationshastighet på x-axeln och vridmoment på y-axeln, färgat efter maskinfel.

Varje diagram ska ha beskrivande rubrik, axelrubriker och enheter.

### Uppgift D – Tolka

Skriv tre observationer och en begränsning. Skilj på vad diagrammet visar och vad som kräver ytterligare belägg.

## Individuellt projektarbete

Ta fram:

- en avgränsad analysfråga,
- vilka kolumner som behövs,
- minst ett behandlingsval,
- minst en relevant feature,
- en första visualisering,
- en prioriterad uppgift inför dag 3.
