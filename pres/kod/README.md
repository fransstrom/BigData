## Frågeställning
Är sambandet mellan verktygsslitage och maskinfel starkare vid högt vridmoment?

### Intressanta kolumner
- Tool wear [min]
- Torque [Nm]
- Machine failure

## Kör analysen

Kör kommandona från projektroten (`BigData`) med din virtuella Pythonmiljö aktiverad:

```bash
python -m pip install -r pres/kod/python/requirements.txt
python pres/kod/python/download_data.py
python pres/kod/python/pres.py --input pres/kod/data/ai4i2020.csv
```

Analysen sparar rensad data i `pres/kod/output/pres_ai4i_clean.csv`, en gruppjämförelse
och ett diagram. Gruppjämförelsen används för att besvara frågeställningen.

## Träna och spara modellen

```bash
python pres/kod/python/train_iot.py
```

Skriptet läser den rensade datan och använder endast verktygsslitage och vridmoment
för att klassificera maskinfel. Ett beslutsträd med maximalt djup 3 tränas på 80 %
av datan. Resterande 20 % används för utvärdering. Uppdelningen är stratifierad
och reproducerbar med `random_state=42`. Trädet kräver minst tio observationer
per löv och använder balanserade klassvikter eftersom maskinfel är ovanliga.

Två filer sparas i `pres/kod/output/`:

- `model.joblib`: den tränade modellen, inklusive namn och ordning på indatakolumnerna.
- `model_metrics.json`: precision, recall, F1, accuracy och antal korrekta
  förutsägelser, upptäckta fel, missade fel och falsklarm för modellen och
  baslinjen ”alltid normal drift”, utvärderade på samma testdata.

Precision, recall och F1 avser klassen maskinfel (1). Måtten anges som andelar
mellan 0 och 1. `correct_normal` räknar korrekt förutsagd normal drift och
`correct_predictions` räknar alla korrekta förutsägelser.

Varje körning tränar på nytt och ersätter modell- och resultatfilen.
En annan rensad CSV kan anges med `--input` och en annan resultatmapp
med `--output`. Modellen kompletterar gruppanalysen med förutsägelser.

## Använd modellen med egna värden

```bash
python pres/kod/python/predict_iot.py --tool-wear 190 --torque 65
```

`--tool-wear` anges i minuter och `--torque` i Nm. Använd punkt som decimaltecken.
Skriptet laddar modellen och skriver ut `Förutsägelse: normal drift` eller
`Förutsägelse: maskinfel`. Det tränar aldrig modellen och behöver inte träningsdatan.
Du kan välja en annan modellfil med `--model sökväg/till/model.joblib`.

Använd samma paketversioner vid träning och prediktion och ladda bara modellfiler
du litar på. `pres/run.sh` kör nedladdning, analys och träning. Kör det från `pres/`
med `bash run.sh`. Prediktionen körs separat.
