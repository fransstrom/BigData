# Övningar dag 3

## Övning 1 – Välj rätt problemtyp

Klassificera varje fall som regression, klassificering, anomalidetektion eller klustring:

1. Förutsäg energianvändning i wattimmar.
    Regression
2. Hitta driftmönster utan färdiga etiketter.
    Klustring
3. Avgör om en AI4I-observation innebär maskinfel.
    klassificering
4. Hitta ovanliga kombinationer av temperatur, varvtal och vridmoment.
    anomalidetektion
5. Uppskatta återstående verktygslivslängd i minuter.
    regression

## Laboration – Klassificera maskinfel

Kör först det färdiga exemplet:

```bash
source .venv/bin/activate
python dag_3/kod/python/download_data.py
python dag_3/kod/python/analyze_iot.py dag_3/kod/data/ai4i2020.csv
python dag_3/kod/python/train_model.py dag_3/kod/output/ai4i_clean.csv
```

Öppna `model_metrics.json` och besvara:

1. Hur stor är felklassen i testdatan?
    test_failure_rate=3.4%    
2. Varför har baslinjen hög accuracy men recall 0?
    baslinjen gissar alltid normal drift. Eftersom de flesta observationerna är normal drift får den hög accuracy. men missar alla 85 verkliga maskinfel. så recall blir 0/85 = 0%
3. Hur många verkliga fel hittar modellen?
    69
4. Hur många falska larm skapar modellen?
    340   
5. Vilket är viktigast här: precision eller recall?
    Jag prioriterar recall för maskinfel eftersom jag vill hitta så många verkliga fel som möjligt. Hög accuracy kan vara missvisande när normal drift är mycket vanligare än maskinfel.
6. När kan en enkel regel vara bättre än modellen?
    Vid enklare featurevärden där ett värde kan vara en anledning till att stoppa/varna för fel. tex temp > 200

## Undersök modellen i Python

```python
import json

with open("dag_3/kod/output/model_metrics.json") as file:
    result = json.load(file)

print(result["model"])
print(result["baseline"])
```

Förvirringsmatrisen har formen:

```text
[[sant normal, falskt larm],
 [missat fel,  hittat fel]]
```

Beräkna hur många procent av de verkliga felen som modellen hittar. Kontrollera att resultatet motsvarar recall.

## Extra – Jämför med en regel

Skapa en enkel regel, till exempel baserad på hög mekanisk effekt eller högt verktygsslitage. Jämför regelns precision och recall med ML-modellen.

Syftet är inte att hitta den perfekta regeln utan att skapa en begriplig baslinje.

## Källövning

Läs UCI:s dokumentation för AI4I och NIST AI RMF:s avsnitt om tillförlitlighet:

- https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset
- https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10 (för hela dokumentet)

Skriv kort:

- Varför skapades AI4I som syntetiskt dataset?
- Vilken begränsning får det för din slutsats?
- Vilken typ av modellfel är mest kostsam i ditt tänkta fall?
- Vilken avvägning mellan precision och recall gör du?

## Individuellt projektarbete

Dokumentera:

- målvariabel och valda features,
- features som utesluts och varför,
- tränings- och teststrategi,
- baslinje och mätetal,
- modellens resultat,
- ett motiverat beslut om praktisk användning.
