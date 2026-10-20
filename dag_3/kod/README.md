# Kod dag 3

## Innehåll

- `python/analyze_iot.py` skapar den behandlade datafilen.
- `python/train_model.py` tränar klassificeringsmodellen och jämför med baslinjen.
- `python/download_data.py` hämtar dagens datafil från UCI.
- `data/` innehåller information om datasetet. CSV-filen ingår inte i studentpaketet.
- `output/` tar emot behandlad data och modellmått.

## Kör

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dag_3/kod/python/requirements.txt
python dag_3/kod/python/download_data.py
python dag_3/kod/python/analyze_iot.py dag_3/kod/data/ai4i2020.csv
python dag_3/kod/python/train_model.py dag_3/kod/output/ai4i_clean.csv
```
