import pandas as pd

data = pd.read_csv("dag_1/kod/data/ai4i2020.csv")
print(data.head())
print(data.dtypes)
print(data.describe())
