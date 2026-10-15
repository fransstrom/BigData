# Kod dag 2

## Innehåll

- `python/analyze_iot.py` behandlar AI4I, skapar features, sammanfattningar och diagram.
- `python/README.md` förklarar `analyze_iot.py` steg för steg.
- `python/download_data.py` hämtar dagens datafil från UCI.
- `data/` innehåller information om datasetet. CSV-filen ingår inte i studentpaketet.
- `output/` tar emot genererade filer.

## Kör

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dag_2/kod/python/requirements.txt
python dag_2/kod/python/download_data.py
python dag_2/kod/python/analyze_iot.py dag_2/kod/data/ai4i2020.csv
```
