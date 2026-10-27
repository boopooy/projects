import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="🍽️ 레스토랑 팁 분석", layout="wide")
st.title("🍽️ 레스토랑 팁 분석")

tips = sns.load_dataset("tips")

st.sidebar.header("차트 설정")
scatter_color_options = {
    "성별(sex)": "sex",
    "흡연여부(smoker)": "smoker",
    "요일(day)": "day",
    "시간대(time)": "time",
}
bar_group_options = {
    "요일(day)": "day",
    "성별(sex)": "sex",
    "시간대(time)": "time",
    "흡연여부(smoker)": "smoker",
}
scatter_color_label = st.sidebar.selectbox(
    "산점도 색상 기준",
    options=list(scatter_color_options),
)
bar_group_label = st.sidebar.selectbox(
    "막대차트 그룹 기준",
    options=list(bar_group_options),
)

st.subheader("섹션 1. 기술 통계 요약")
metric_columns = st.columns(4)
metric_columns[0].metric("총 데이터 수", f"{len(tips):,}")
metric_columns[1].metric("평균 식사 금액", f"${tips['total_bill'].mean():.2f}")
metric_columns[2].metric("평균 팁 금액", f"${tips['tip'].mean():.2f}")
average_tip_percentage = tips["tip"].div(tips["total_bill"]).mean() * 100
metric_columns[3].metric("평균 팁 비율", f"{average_tip_percentage:.2f}%")
st.dataframe(tips.describe())

st.subheader("섹션 2. 금액 vs 팁 산점도")
scatter_fig = px.scatter(
    tips,
    x="total_bill",
    y="tip",
    color=scatter_color_options[scatter_color_label],
    hover_data=["total_bill", "tip", "size"],
    trendline="ols",
    labels={
        "total_bill": "식사 금액 ($)",
        "tip": "팁 금액 ($)",
        "size": "인원수",
        "sex": "성별",
        "smoker": "흡연 여부",
        "day": "요일",
        "time": "시간대",
    },
)
st.plotly_chart(scatter_fig, use_container_width=True)

st.subheader("섹션 3. 조건별 합계 막대차트")
bar_group_column = bar_group_options[bar_group_label]
grouped_bills = (
    tips.groupby(bar_group_column, as_index=False, observed=True)["total_bill"]
    .sum()
)
bar_fig = px.bar(
    grouped_bills,
    x=bar_group_column,
    y="total_bill",
    text="total_bill",
    title="선택 기준별 총 식사 금액 합계",
    labels={
        bar_group_column: bar_group_label,
        "total_bill": "식사 금액 합계 ($)",
    },
)
bar_fig.update_traces(
    texttemplate="$%{text:,.2f}",
    textposition="outside",
    cliponaxis=False,
)
st.plotly_chart(bar_fig, use_container_width=True)
