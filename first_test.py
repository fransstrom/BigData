import pandas as pd
data = pd.read_csv("dag_1/kod/data/ai4i2020.csv", encoding="utf-8-sig")

print(data.head())
print(data.shape)
print(data.columns)
print(data.dtypes)
print(data.isna().sum())
print(data.duplicated().sum())
print(data.describe())

