import pandas as pd

df = pd.read_csv("./data/pension_raw.csv", encoding='cp949')
df.info()