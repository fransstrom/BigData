# Förklaring av `analyze_iot.py`

`analyze_iot.py` läser AI4I-data, kontrollerar och rensar rader, skapar två nya features, sammanfattar datan och sparar ett diagram samt flera resultatfiler.

Skriptet är ett exempel på en enkel datapipeline på en dator:

```text
CSV-fil -> inläsning -> kvalitetskontroll -> features -> aggregat -> filer och diagram
```

Det är inte ett distribuerat Big Data-system. Samma arbetssteg återkommer däremot i större lösningar, där lagring och beräkning kan vara fördelade över flera datorer.

## Förberedelser

Kör från roten av `BigData`-mappen:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dag_2/kod/python/requirements.txt
python dag_2/kod/python/download_data.py
```

På Windows aktiveras miljön normalt med:

```powershell
.venv\Scripts\activate.ps1
```

## Kör skriptet

```bash
python dag_2/kod/python/analyze_iot.py \
  dag_2/kod/data/ai4i2020.csv
```

Det första argumentet efter skriptnamnet är sökvägen till indatafilen.

En annan utdatakatalog kan anges med `--output`:

```bash
python dag_2/kod/python/analyze_iot.py \
  dag_2/kod/data/ai4i2020.csv \
  --output min_indata
```

## Indata

Skriptet förväntar sig AI4I-filens ursprungliga kolumnnamn. De viktigaste är:

| Kolumn | Betydelse |
|---|---|
| `UDI` | Unikt rad-ID |
| `Product ID` | Produktidentifierare |
| `Type` | Produktvariant L, M eller H |
| `Air temperature [K]` | Lufttemperatur i kelvin |
| `Process temperature [K]` | Processtemperatur i kelvin |
| `Rotational speed [rpm]` | Rotationshastighet i varv per minut |
| `Torque [Nm]` | Vridmoment i newtonmeter |
| `Tool wear [min]` | Verktygsslitage uttryckt i minuter |
| `Machine failure` | 0 för normal drift och 1 för maskinfel |

## Kodens delar

### 1. Importer och sökvägar

```python
import argparse
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
```

Biblioteken används till följande:

* `argparse` läser argument från terminalen
* `json` skapar kvalitetsrapporten
* `os` används för Matplotlibs konfigurationskatalog
* `Path` hanterar filsökvägar på ett portabelt sätt
* `matplotlib.pyplot` skapar diagram
* `pandas` läser och behandlar tabeller

`CODE_DIR` räknas fram från skriptets egen plats. Därför kan standardmappen `dag_2/kod/output` hittas även om kommandot startas från en annan mapp.

`MPLCONFIGDIR` anger var Matplotlib får spara sin lokala cache. Raden måste köras innan `matplotlib.pyplot` importeras.

### 2. Begripliga kolumnnamn

```python
RENAME = {
    "Air temperature [K]": "air_temperature_k",
    "Rotational speed [rpm]": "rotational_speed_rpm",
    "Machine failure": "machine_failure",
}
```

Den riktiga ordlistan innehåller fler kolumner. Vänster sida är namnet i originalfilen och höger sida namnet som används i analysen. Namn med små bokstäver och understreck är enklare att skriva i Python. Enheten behålls i namnet när den är viktig.

### 3. Kommandoradsargument

```python
parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("--output", type=Path, default=CODE_DIR / "output")
args = parser.parse_args()
```

`input` är obligatoriskt och innehåller sökvägen till CSV-filen. `--output` är frivilligt. Om det utelämnas används `dag_2/kod/output`.

Efter `parse_args()` finns värdena i `args.input` och `args.output`.

### 4. Läs in data

```python
data = pd.read_csv(args.input, encoding="utf-8-sig").rename(columns=RENAME)
```

`pd.read_csv` läser CSV-filen till en `DataFrame`, en tabell i minnet. `encoding="utf-8-sig"` hanterar även en eventuell UTF-8-markör i början av filen. `rename` byter kolumnnamn enligt ordlistan.

### 5. Räkna och ta bort dubbletter

```python
original_rows = len(data)
duplicate_rows = int(data.duplicated().sum())
data = data.drop_duplicates().copy()
```

`len(data)` ger antalet rader. `duplicated()` ger `True` för hela dubblettrader och `sum()` räknar dem. `drop_duplicates()` tar bort dubbletterna.

`.copy()` skapar en självständig tabell. Det minskar risken för otydliga ändringar och varningar när nya kolumner skapas senare.

### 6. Kontrollera rimliga värden

```python
valid = (
    data["air_temperature_k"].between(250, 350)
    & data["process_temperature_k"].between(250, 400)
    & data["rotational_speed_rpm"].gt(0)
    & data["torque_nm"].ge(0)
    & data["tool_wear_min"].ge(0)
    & data["machine_failure"].isin([0, 1])
)
```

Varje kontroll ger `True` eller `False` för varje rad:

* `between(250, 350)` kräver ett värde inom intervallet, inklusive gränserna
* `gt(0)` betyder större än noll
* `ge(0)` betyder större än eller lika med noll
* `isin([0, 1])` tillåter bara värdena 0 och 1
* `&` betyder att samtliga villkor måste vara sanna

Resultatet `valid` kallas en boolesk mask. Den används för att välja giltiga rader:

```python
clean = data.loc[valid].copy()
```

Gränserna är explicita så att de kan granskas och ändras. Att koden kör utan fel betyder inte automatiskt att gränserna är rätt för en verklig maskin.

### 7. Skapa nya features

```python
clean["power_w"] = (
    clean["torque_nm"]
    * clean["rotational_speed_rpm"]
    * 2
    * 3.141592653589793
    / 60
)
```

Mekanisk effekt beräknas som vridmoment gånger vinkelhastighet. Faktorn `2π / 60` omvandlar varv per minut till radianer per sekund. Resultatet får enheten watt.

```python
clean["temperature_difference_k"] = (
    clean["process_temperature_k"] - clean["air_temperature_k"]
)
```

Temperaturskillnaden visar hur mycket varmare processen är än omgivande luft. Pandas utför båda beräkningarna för samtliga rader utan att vi skriver en egen loop.

### 8. Gruppera och sammanfatta

```python
summary = clean.groupby("type").agg(
    observations=("udi", "size"),
    failures=("machine_failure", "sum"),
    failure_rate=("machine_failure", "mean"),
    mean_torque_nm=("torque_nm", "mean"),
)
```

`groupby("type")` skapar en grupp för H, L och M. `agg` beräknar flera mått per grupp. Eftersom `machine_failure` består av nollor och ettor ger summan antalet fel och medelvärdet felandelen.

Det fullständiga skriptet beräknar även genomsnittlig lufttemperatur och rotationshastighet.

### 9. Skapa kvalitetsrapporten

```python
quality = {
    "source_rows": original_rows,
    "duplicate_rows": duplicate_rows,
    "clean_rows": len(clean),
}
```

Den fullständiga ordlistan innehåller också antal saknade värden, ogiltiga rader, maskinfel och felandel. Informationen gör behandlingen lättare att kontrollera och återskapa.

### 10. Skapa utdatakatalog och filer

```python
args.output.mkdir(parents=True, exist_ok=True)
```

Raden skapar utdatakatalogen och eventuella saknade överordnade kataloger. `exist_ok=True` gör att kommandot inte ger fel om katalogen redan finns.

`to_csv` sparar tabellerna. `json.dumps` omvandlar kvalitetsrapporten till JSON. Diagrammet sparas med `fig.savefig`.

### 11. Skapa diagram

```python
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
```

Raden skapar en figur med två diagram bredvid varandra. `axes[0]` används för punktdiagrammet och `axes[1]` för stapeldiagrammet.

Normal drift ritas med små, genomskinliga punkter eftersom den gruppen dominerar. Maskinfel ritas tydligare. Stapeldiagrammet visar felandel i procent per produkttyp.

`tight_layout()` justerar avstånd så att texter inte överlappar. `savefig(..., dpi=160)` sparar bilden med tillräcklig upplösning för skärm och presentation.

### 12. Startpunkten

```python
if __name__ == "__main__":
    main()
```

Villkoret anropar `main()` när filen körs direkt. Om filen i stället importeras från ett annat Pythonprogram startar inte hela analysen automatiskt.

## Filer som skapas

| Fil | Innehåll |
|---|---|
| `ai4i_clean.csv` | Rensade rader och de två nya features-kolumnerna |
| `summary_by_type.csv` | Sammanfattning per produkttyp |
| `machine_failures.csv` | Endast rader där maskinfel är 1 |
| `quality_report.json` | Antal rader, kvalitetskontroller och felandel |
| `ai4i_overview.png` | Punktdiagram och felandel per produkttyp |

När originalfilen används ska rapporten visa 10 000 källrader, 0 dubbletter, 0 saknade värden, 0 ogiltiga rader och 339 maskinfel.

## Vanliga fel

### `No such file or directory`

Kontrollera att kommandot körs från roten av `BigData` och att nedladdningsskriptet har körts.

### `ModuleNotFoundError`

Aktivera `.venv` och installera `requirements.txt`.

### `KeyError` för en kolumn

Skriptet förväntar sig AI4I-filens ursprungliga kolumnnamn. Kontrollera att rätt fil används och att rubrikraden inte har ändrats.

### Diagrammet visas inte i ett fönster

Skriptet sparar diagrammet som `ai4i_overview.png`. Det behöver inte öppna ett interaktivt fönster.

## Viktiga begränsningar

* AI4I är syntetiskt och visar inte automatiskt hur en verklig maskinpark fungerar
* Rimlighetsgränserna är undervisningsexempel och behöver domänvalideras
* Skriptet läser hela filen i minnet på en dator
* Diagrammen visar samband, inte orsak
* Feltypskolumnerna finns kvar för spårbarhet men bör inte användas för att förutsäga `machine_failure`, eftersom de läcker svaret
