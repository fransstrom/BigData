# Kod dag 1

## Innehåll

- `python/download_data.py` hämtar AI4I från UCI.
- `python/inspect_data.py` visar rader, kolumner, datatyper, saknade värden, dubbletter och felandel.
- `python/requirements.txt` innehåller Pythonberoenden.
- `data/` innehåller information om datasetet. Själva CSV-filen hämtar du enligt stegen nedan.

## Kör

Kör från kursens rotmapp. Skapa miljön första gången:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dag_1/kod/python/requirements.txt
```

Hämta datafilen och kör sedan inspektionen:

```bash
python dag_1/kod/python/download_data.py
python dag_1/kod/python/inspect_data.py
```
