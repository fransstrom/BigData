# Övningar dag 1

## Övning 1 – Hur stor blir datan?

En anläggning har 2 500 maskiner. Varje maskin producerar ett meddelande på 160 byte två gånger per sekund.

Beräkna ungefär byte per sekund, GB per dygn och TB per år. Hur förändras lagringsbehovet om systemet sparar tre kopior?
Byte/s = 2500 * 2 * 160 = 800 000 byte/s
GB/s = 800000 / 1000000000 = 0.0008 GB/s
sekunder/år = 60 * 60 * 24 * 365 = 31536000 s
GB/dygn = 0.0008 * 86400 = 69.12 GB
GB/år = 0.0008 * 31536000 = 25228.8 GB = ca 25.23 TB

Skriv också två antaganden som beräkningen inte tar hänsyn till.
Skottår och drifttid

## Övning 2 – Läs datasetets dokumentation

Öppna UCI-sidan:

https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

Besvara:

1. Är datan verklig eller syntetisk?
    Står på hemsidan att den är syntetisk
2. Vad representerar en rad?
    I AI4I-datasetet representerar en rad en simulerad observation av en tillverkningsprocess, kopplad till en produkt 
3. Vilka kolumner är mätvärden?
    Air temp, process temp, rotational speed, torque, tool wear
4. Vilken kolumn är målvariabel?
    Machine failure
5. Vilka kolumner är identifierare?
    UID, Produkt ID
6. Vilka kolumner riskerar att läcka svaret till en ML-modell?
    Alla kolumner i machine failure kategorin.
7. Vilken licens gäller?
    This dataset is licensed under a Creative Commons Attribution 4.0 International (CC BY 4.0) license.

## Laboration – Första mötet med AI4I

Aktivera miljön och hämta datan vid behov:

```bash
source .venv/bin/activate
python dag_1/kod/python/download_data.py
```

```python
import pandas as pd

data = pd.read_csv("dag_1/kod/data/ai4i2020.csv", encoding="utf-8-sig")

print(data.head())
print(data.shape)
print(data.columns)
print(data.dtypes)
print(data.isna().sum())
print(data.duplicated().sum())
print(data.describe())
```

Besvara:

1. Hur många rader och kolumner finns?
    10 000 rader, 14 kolumner
2. Finns saknade värden eller dubbletter?
    Nej.
3. Hur stor andel av raderna har `Machine failure == 1`?
    3.39%
4. Vad betyder `Type`?
    Producerad produkts kvalitet (low, medium, high)
5. Varför bör `UDI` och `Product ID` normalt inte användas som numeriska features
    De är identifierare, inte värden som hjälper modellen att förutspå machine failure etc
6. Varför kan `TWF`, `HDF`, `PWF`, `OSF` och `RNF` ge dataläckage?
    För att det är värdena som ML ska förutsåp. Om de skickas med så får modellen ledtrådar som den inte har under vanlig körning

Beräkna felandelen:

```python
failure_rate = data["Machine failure"].mean()
print(f"Andel maskinfel: {failure_rate:.2%}")
```

## Individuell projektstart

Skriv högst en sida med:

- valt dataset och länk till källan,
- vad en rad representerar,
- en avgränsad analysfråga,
- tre relevanta kolumner,
- ett kvalitets- eller urvalsproblem,
- en tänkbar visualisering.

## Exit ticket

https://mentorsparks.com/g/2xhUdw

Svara individuellt:

1. Vad är den största begränsningen med datasetet?
2. Vilken kolumn behöver du förstå bättre?
3. Vilken analysfråga vill du arbeta vidare med?
4. Vad vill du repetera nästa lektion?
