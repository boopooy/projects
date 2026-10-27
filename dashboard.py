import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st


st.set_page_config(page_title="통합 분석 대시보드", layout="wide")

flights_tab, tips_tab = st.tabs(["✈️ 항공 승객 분석", "🍽️ 레스토랑 팁 분석"])

with flights_tab:
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

with tips_tab:
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
