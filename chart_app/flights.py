import plotly.express as px
import pandas as pd
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="✈️ 항공 승객 분석", layout="wide")
st.title("✈️ 항공 승객 분석")

flights = sns.load_dataset("flights")
months = list(flights["month"].cat.categories)
month_numbers = {month: number for number, month in enumerate(months, start=1)}
flights["month_number"] = flights["month"].map(month_numbers).astype("int64")

metric_columns = st.columns(3)
metric_columns[0].metric("총 행 수", f"{len(flights):,}")
metric_columns[1].metric(
    "연도 범위",
    f"{flights['year'].min()}–{flights['year'].max()}",
)
metric_columns[2].metric("최대 승객 수", f"{flights['passengers'].max():,}")

with st.sidebar:
    month_range = st.slider(
        "월 범위",
        min_value=1,
        max_value=12,
        value=(1, 12),
        format="%d월",
    )

filtered_flights = flights.loc[
    flights["month_number"].between(month_range[0], month_range[1])
]
yearly_average = (
    filtered_flights.groupby("year", as_index=False, observed=True)["passengers"]
    .mean()
    .rename(columns={"passengers": "평균 승객 수"})
    .sort_values("year")
)
yearly_average["3년 이동평균"] = yearly_average["평균 승객 수"].rolling(window=3).mean()
yearly_lines = yearly_average.melt(
    id_vars="year",
    value_vars=["평균 승객 수", "3년 이동평균"],
    var_name="지표",
    value_name="승객 수",
)

st.subheader("연도별 평균 승객 수 및 3년 이동평균")
fig_yearly = px.line(
    yearly_lines,
    x="year",
    y="승객 수",
    color="지표",
    line_dash="지표",
    line_dash_map={"평균 승객 수": "solid", "3년 이동평균": "dash"},
    labels={"year": "연도", "승객 수": "평균 승객 수", "지표": ""},
    markers=True,
)
st.plotly_chart(fig_yearly, use_container_width=True)

monthly_average = (
    flights.groupby("month", observed=False, as_index=False)["passengers"]
    .mean()
    .rename(columns={"passengers": "평균 승객 수"})
)
monthly_average["월 순서"] = monthly_average["month"].map(month_numbers)
monthly_average = monthly_average.sort_values("월 순서")

st.subheader("월별 평균 승객 수")
fig_monthly = px.bar(
    monthly_average,
    x="month",
    y="평균 승객 수",
    category_orders={"month": months},
    labels={"month": "월"},
)
st.plotly_chart(fig_monthly, use_container_width=True)

st.subheader("월별 승객 수 분포")
fig_box = px.box(
    flights,
    x="month",
    y="passengers",
    category_orders={"month": months},
    labels={"month": "월", "passengers": "승객 수"},
)
st.plotly_chart(fig_box, use_container_width=True)

st.subheader("연도/월별 승객 수 히트맵")
flight_pivot = flights.pivot_table(
    index="year",
    columns="month",
    values="passengers",
    observed=False,
)
flight_pivot = flight_pivot.reindex(columns=months).sort_index()
fig_heatmap = px.imshow(
    flight_pivot,
    x=months,
    y=flight_pivot.index,
    color_continuous_scale="Blues",
    labels={"x": "월", "y": "연도", "color": "승객 수"},
    aspect="auto",
    text_auto=True,
)
st.plotly_chart(fig_heatmap, use_container_width=True)
