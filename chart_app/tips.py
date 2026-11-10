import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="🍽️ 레스토랑 팁 분석", layout="wide")
st.title("🍽️ 레스토랑 팁 분석")

tips = sns.load_dataset("tips")
tips["tip_rate"] = tips["tip"] / tips["total_bill"] * 100

st.subheader("기술 통계 요약")
metric_columns = st.columns(4)
metric_columns[0].metric("총 데이터 수", f"{len(tips):,}")
metric_columns[1].metric("평균 식사 금액", f"${tips['total_bill'].mean():.2f}")
metric_columns[2].metric("평균 팁 금액", f"${tips['tip'].mean():.2f}")
metric_columns[3].metric("평균 팁 비율", f"{tips['tip_rate'].mean():.2f}%")
st.dataframe(tips.describe(), use_container_width=True)

color_options = {
    "성별(sex)": "sex",
    "흡연여부(smoker)": "smoker",
    "요일(day)": "day",
    "시간대(time)": "time",
}
group_options = {
    "요일(day)": "day",
    "성별(sex)": "sex",
    "시간대(time)": "time",
    "흡연여부(smoker)": "smoker",
}

with st.sidebar:
    color_label = st.selectbox("산점도 색상 기준", list(color_options))
    group_label = st.selectbox("막대차트 그룹 기준", list(group_options))

st.subheader("식사 금액과 팁의 관계")
fig_scatter = px.scatter(
    tips,
    x="total_bill",
    y="tip",
    color=color_options[color_label],
    hover_data={"total_bill": ":.2f", "tip": ":.2f", "size": True},
    trendline="ols",
    labels={
        "total_bill": "식사 금액 ($)",
        "tip": "팁 금액 ($)",
        color_options[color_label]: color_label,
    },
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("선택 기준별 총 식사 금액 합계")
group_column = group_options[group_label]
bill_totals = (
    tips.groupby(group_column, observed=False, as_index=False)["total_bill"]
    .sum()
    .rename(columns={"total_bill": "총 식사 금액"})
)
fig_bar = px.bar(
    bill_totals,
    x=group_column,
    y="총 식사 금액",
    text_auto=".2f",
    title="선택 기준별 총 식사 금액 합계",
    labels={group_column: group_label, "총 식사 금액": "총 식사 금액 ($)"},
)
st.plotly_chart(fig_bar, use_container_width=True)
