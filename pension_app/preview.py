import pandas as pd

df = pd.read_csv("data/pension_raw.csv", encoding="cp949")

print("첫 다섯 행:")
print(df.head())

print("\n컬럼 이름 목록:")
print(df.columns.tolist())

print("\n컬럼별 데이터 타입:")
print(df.dtypes)

rows, columns = df.shape
print(f"\n전체 행 수: {rows}")
print(f"전체 컬럼 수: {columns}")

print("\n컬럼별 결측값(NaN) 개수:")
print(df.isna().sum())