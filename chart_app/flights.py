import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="✈️ 항공 승객 분석", layout="wide")
st.title("✈️ 항공 승객 분석")

flights = sns.load_dataset("flights")
month_abbreviations = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
month_labels = [f"{number}월" for number in range(1, 13)]
month_to_number = {
    month: number for number, month in enumerate(month_abbreviations, start=1)
}

flights["month_number"] = flights["month"].map(month_to_number).astype(int)
flights["month_name"] = pd.Categorical(
    flights["month_number"].map(lambda month_number: month_labels[month_number - 1]),
    categories=month_labels,
    ordered=True,
)

metric_columns = st.columns(3)
metric_columns[0].metric("총 행 수", f"{len(flights):,}")
metric_columns[1].metric(
    "연도 범위",
    f"{flights['year'].min()}–{flights['year'].max()}",
)
metric_columns[2].metric("최대 승객 수", f"{flights['passengers'].max():,}")

month_range = st.sidebar.slider(
    "월 범위",
    min_value=1,
    max_value=12,
    value=(1, 12),
    format="%d월",
)

selected_flights = flights[
    flights["month_number"].between(month_range[0], month_range[1])
]
yearly_average = (
    selected_flights.groupby("year", as_index=False, observed=True)["passengers"]
    .mean()
    .rename(columns={"passengers": "평균 승객 수"})
    .sort_values("year")
)
yearly_average["3년 이동평균"] = yearly_average["평균 승객 수"].rolling(window=3).mean()
yearly_chart_data = yearly_average.melt(
    id_vars="year",
    value_vars=["평균 승객 수", "3년 이동평균"],
    var_name="구분",
    value_name="승객 수",
)

st.subheader("차트 1. 연도별 평균 승객 수")
yearly_fig = px.line(
    yearly_chart_data,
    x="year",
    y="승객 수",
    color="구분",
    labels={"year": "연도", "승객 수": "평균 승객 수"},
    markers=True,
)
yearly_fig.update_traces(
    line={"dash": "dot"},
    selector={"name": "3년 이동평균"},
)
st.plotly_chart(yearly_fig, use_container_width=True)

monthly_average = (
    flights.groupby("month_number", as_index=False, observed=True)["passengers"]
    .mean()
    .sort_values("month_number")
)
monthly_average["month_name"] = monthly_average["month_number"].map(
    lambda month_number: month_labels[month_number - 1]
)

st.subheader("차트 2. 월별 평균 승객 수")
monthly_fig = px.bar(
    monthly_average,
    x="month_name",
    y="passengers",
    category_orders={"month_name": month_labels},
    labels={"month_name": "월", "passengers": "평균 승객 수"},
)
st.plotly_chart(monthly_fig, use_container_width=True)

st.subheader("차트 3. 월별 승객 수 분포")
box_fig = px.box(
    flights,
    x="month_name",
    y="passengers",
    category_orders={"month_name": month_labels},
    labels={"month_name": "월", "passengers": "승객 수"},
)
st.plotly_chart(box_fig, use_container_width=True)

heatmap_data = flights.pivot_table(
    index="year",
    columns="month_number",
    values="passengers",
    aggfunc="mean",
    observed=True,
).reindex(columns=range(1, 13))
heatmap_data.columns = month_labels

st.subheader("차트 4. 연도별·월별 승객 수 히트맵")
heatmap_fig = px.imshow(
    heatmap_data,
    x=month_labels,
    y=heatmap_data.index,
    text_auto=True,
    color_continuous_scale="Blues",
    aspect="auto",
    labels={"x": "월", "y": "연도", "color": "승객 수"},
)
st.plotly_chart(heatmap_fig, use_container_width=True)
