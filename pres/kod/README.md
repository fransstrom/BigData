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
python pres/kod/python/pres.py pres/kod/data/ai4i2020.csv
```

Analysen sparar rensad data i `pres/kod/output/ai4i_clean.csv`, en gruppjämförelse
och ett diagram. Gruppjämförelsen används för att besvara frågeställningen.

## Träna och spara modellen

```bash
python pres/kod/python/train_iot.py
```

Skriptet läser den rensade datan och använder endast verktygsslitage och vridmoment
för att klassificera maskinfel. 80 % av datan används för träning och modellval.
Resterande 20 % används för slututvärdering. Uppdelningen är stratifierad
och reproducerbar med `random_state=42`.

`GridSearchCV` jämför automatiskt 36 kombinationer:

- `max_depth`: 3, 5 eller 7.
- `min_samples_leaf`: 5, 10 eller 20.
- `class_weight`: `None`, `{0: 1, 1: 5}`, `{0: 1, 1: 10}` eller `"balanced"`.

Varje kombination utvärderas med femfaldig stratifierad korsvalidering inom
träningsdatan, med samma uppdelningar för alla kombinationer. Det ger 180
träningskörningar. Modellen väljs utifrån minst 80 % genomsnittlig recall vid
korsvalideringen (`MIN_RECALL` i skriptet). Bland kombinationerna som når målet
väljs högst genomsnittlig precision, därefter högst recall vid lika precision.
Om ingen når målet väljs högst recall, därefter precision, och skriptet skriver
tydligt att målet inte uppnåddes. Gränsen gäller genomsnittet över valideringsdelarna
och garanterar inte 80 % recall på nya data.
F1 rapporteras fortfarande som jämförelse men styr inte valet. Det är det harmoniska
medelvärdet av precision och recall: `2 * precision * recall / (precision + recall)`.
Vinnaren tränas därefter på hela träningsmängden och utvärderas på testdatan.
Målet är att hitta många maskinfel och därefter begränsa falsklarmen bland de
prövade kombinationerna. Höga nivåer av både recall och precision kan inte garanteras.

Tre filer sparas i `pres/kod/output/`:

- `model.joblib`: den tränade modellen, inklusive namn och ordning på indatakolumnerna.
- `model_metrics.json`: precision, recall, F1, accuracy och antal korrekta
  förutsägelser, upptäckta fel, missade fel och falsklarm för modellen och
  baslinjen ”alltid normal drift”, utvärderade på samma testdata. Under `search`
  sparas urvalsregeln, recall-målet, om målet uppnåddes, valda inställningar och
  genomsnittlig precision, recall och F1 vid korsvalideringen.
- `model_search.csv`: alla 36 kombinationer, med de som klarar recall-målet först,
  därefter sorterade efter precision och recall. Om ingen når målet sorteras hela
  tabellen efter recall och precision. `selection_rank` visar ordningen och
  `selected` markerar vinnaren. Tabellen visar också om recall-målet uppnåtts,
  inställningar, genomsnittlig precision, recall och F1 samt standardavvikelser
  för recall och F1 mellan de fem valideringsdelarna.

`mean_test_*` i söktabellen avser valideringsdelarna inom träningsdatan, inte de
separata testobservationerna. Använd sökresultaten för modellval och håll testdatan
utanför sökningen. Vid helt lika precision och recall väljs den första
kombinationen i sökordningen.

Precision, recall och F1 avser klassen maskinfel (1). Måtten anges som andelar
mellan 0 och 1. `correct_normal` räknar korrekt förutsagd normal drift och
`correct_predictions` räknar alla korrekta förutsägelser.

Varje körning gör om sökningen och ersätter modellfilen och båda resultatfilerna.
En annan rensad CSV kan anges som positionsargument och en annan resultatmapp
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
du litar på. Träning och prediktion körs separat; `pres/run.sh` kör fortsatt bara
nedladdning och analys.
