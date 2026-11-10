from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "cleaned_pension.csv"
ZIP_DATA_PATH = DATA_PATH.with_suffix(".zip")
PENSION_RATE = 0.095
SALARY_CAP = 6_590_000

REQUIRED_COLUMNS = {
    "status",
    "member_count",
    "charge_amount",
    "company_type",
    "sido",
    "industry",
    "estimated_salary_per",
}


@st.cache_data
def load_data(file_path: str, zip_file_path: str) -> pd.DataFrame:
    csv_path = Path(file_path)
    if csv_path.is_file():
        return pd.read_csv(csv_path, encoding="utf-8-sig")

    zip_path = Path(zip_file_path)
    if zip_path.is_file():
        return pd.read_csv(zip_path, encoding="utf-8-sig", compression="zip")

    raise FileNotFoundError(f"CSV 또는 압축 파일을 찾을 수 없습니다: {csv_path}")


def main() -> None:
    st.set_page_config(page_title="📋 국민연금 사업장 분석 대시보드", layout="wide")
    st.title("📋 국민연금 사업장 분석 대시보드")

    try:
        data = load_data(str(DATA_PATH), str(ZIP_DATA_PATH))
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        st.error(f"전처리된 데이터를 불러오지 못했습니다: {error}")
        st.stop()

    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        st.error(f"데이터에 필요한 컬럼이 없습니다: {', '.join(sorted(missing_columns))}")
        st.stop()

    for column in ("member_count", "charge_amount", "estimated_salary_per"):
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        invalid_values = data[column].notna() & numeric_values.isna()
        if invalid_values.any():
            st.error(f"'{column}' 컬럼에 숫자로 변환할 수 없는 값이 있습니다.")
            st.stop()
        data[column] = numeric_values.fillna(0)

    registered_data = data.loc[data["status"] == "등록"].copy()

    with st.sidebar:
        st.header("지역 선택")
        sido_options = sorted(data["sido"].dropna().unique().tolist())
        if not sido_options:
            st.error("'sido' 컬럼에 선택할 지역이 없습니다.")
            st.stop()
        selected_sido = st.selectbox("시도", options=sido_options)

        st.header("분석 필터")
        selected_type = st.selectbox("사업장 형태", options=["전체", "법인", "개인"])
        minimum_members = st.slider("최소 가입자 수", min_value=1, max_value=100, value=1)

    total_members = registered_data["member_count"].sum()
    if total_members > 0:
        per_member_salary = (
            registered_data["charge_amount"]
            .div(PENSION_RATE)
            .div(registered_data["member_count"].where(registered_data["member_count"] > 0))
            .clip(upper=SALARY_CAP)
        )
        average_salary = (
            per_member_salary.mul(registered_data["member_count"]).sum() / total_members
        )
    else:
        average_salary = 0

    total_companies, members, salary = st.columns(3)
    total_companies.metric("총 등록 사업장 수", f"{len(registered_data):,}")
    members.metric("총 가입자 수", f"{total_members:,.0f}")
    salary.metric("전국 평균 1인당 추정 월급여", f"{average_salary:,.0f}원")

    filtered_data = registered_data.loc[
        (registered_data["sido"] == selected_sido)
        & (registered_data["member_count"] >= minimum_members)
    ].copy()
    if selected_type != "전체":
        filtered_data = filtered_data.loc[filtered_data["company_type"] == selected_type]

    regional_members = filtered_data["member_count"].sum()
    if regional_members > 0:
        regional_per_member_salary = (
            filtered_data["charge_amount"]
            .div(PENSION_RATE)
            .div(filtered_data["member_count"].where(filtered_data["member_count"] > 0))
            .clip(upper=SALARY_CAP)
        )
        regional_average_salary = (
            regional_per_member_salary.mul(filtered_data["member_count"]).sum()
            / regional_members
        )
    else:
        regional_average_salary = 0

    salary_delta = regional_average_salary - average_salary
    st.subheader(f"{selected_sido} 지역 요약")
    regional_company_metric, regional_member_metric, regional_salary_metric, salary_delta_metric = (
        st.columns(4)
    )
    regional_company_metric.metric("해당 시도 사업장 수", f"{len(filtered_data):,}")
    regional_member_metric.metric("해당 시도 총 가입자 수", f"{regional_members:,.0f}")
    regional_salary_metric.metric(
        "해당 시도 평균 1인당 추정 월급여",
        f"{regional_average_salary:,.0f}원",
    )
    salary_delta_metric.metric(
        "전국 평균 대비 차이",
        delta=f"{salary_delta:+,.0f}원",
        value="차이",
        delta_color="normal",
    )

    st.subheader(f"{selected_sido} 사업장 분석")
    st.caption(
        f"선택 조건에 해당하는 사업장 {len(filtered_data):,}곳 "
        f"(최소 가입자 {minimum_members:,}명"
        f"{f', {selected_type}' if selected_type != '전체' else ''})"
    )

    filtered_data["industry"] = filtered_data["industry"].fillna("업종 정보 없음")
    st.subheader("선택 시도 업종별 사업장 수 TOP 10")
    regional_industry_count = (
        filtered_data.groupby("industry", as_index=False)
        .size()
        .rename(columns={"size": "company_count"})
        .nlargest(10, "company_count")
        .sort_values("company_count", ascending=True)
    )
    company_count_chart = px.bar(
        regional_industry_count,
        x="company_count",
        y="industry",
        orientation="h",
        title="선택 시도 업종별 사업장 수 TOP 10",
        labels={"company_count": "사업장 수", "industry": "업종명"},
        text="company_count",
        template="plotly_white",
    )
    company_count_chart.update_traces(
        texttemplate="%{x:,.0f}",
        textposition="outside",
    )
    company_count_chart.update_yaxes(
        categoryorder="array",
        categoryarray=regional_industry_count["industry"].tolist(),
    )
    company_count_chart.update_layout(
        xaxis_title="사업장 수",
        yaxis_title=None,
        margin=dict(l=10, r=30, t=55, b=10),
    )
    st.plotly_chart(company_count_chart, width="stretch")

    st.subheader("선택 시도 업종별 평균 추정 월급여 TOP 10")
    regional_industry_salary = (
        filtered_data.groupby("industry", as_index=False)["estimated_salary_per"]
        .mean()
        .nlargest(10, "estimated_salary_per")
        .sort_values("estimated_salary_per", ascending=True)
    )
    regional_industry_salary["salary_label"] = regional_industry_salary[
        "estimated_salary_per"
    ].map(lambda value: f"{value:,.0f}원")
    salary_chart = px.bar(
        regional_industry_salary,
        x="estimated_salary_per",
        y="industry",
        orientation="h",
        title="선택 시도 업종별 평균 추정 월급여 TOP 10",
        labels={"estimated_salary_per": "평균 추정 월급여 (원)", "industry": "업종명"},
        text="salary_label",
        template="plotly_white",
    )
    salary_chart.update_traces(textposition="outside", cliponaxis=False)
    salary_chart.update_yaxes(
        categoryorder="array",
        categoryarray=regional_industry_salary["industry"].tolist(),
    )
    salary_chart.add_vline(
        x=SALARY_CAP,
        line_dash="dash",
        line_color="red",
        annotation_text="기준소득 상한액 6,590,000원",
        annotation_position="top",
    )
    salary_chart.update_layout(
        xaxis_title="평균 추정 월급여 (원)",
        yaxis_title=None,
        margin=dict(l=10, r=30, t=55, b=10),
    )
    st.plotly_chart(salary_chart, width="stretch")

    if filtered_data.empty:
        st.info("선택한 조건에 해당하는 사업장이 없습니다. 필터를 변경해 보세요.")
        return

    industry_summary = (
        filtered_data.groupby("industry", as_index=False)["member_count"]
        .sum()
        .nlargest(10, "member_count")
        .sort_values("member_count", ascending=True)
    )

    chart_columns = st.columns(2)
    with chart_columns[0]:
        st.subheader("업종별 가입자 수 상위 10개")
        industry_chart = px.bar(
            industry_summary,
            x="member_count",
            y="industry",
            orientation="h",
            labels={"member_count": "가입자 수", "industry": "업종"},
            text="member_count",
            template="plotly_white",
        )
        industry_chart.update_traces(texttemplate="%{x:,.0f}", textposition="outside")
        industry_chart.update_layout(
            yaxis_title=None,
            xaxis_title="가입자 수",
            margin=dict(l=10, r=20, t=10, b=10),
        )
        st.plotly_chart(industry_chart, width="stretch")

    with chart_columns[1]:
        st.subheader("사업장 형태별 사업장 수")
        type_summary = (
            filtered_data["company_type"]
            .fillna("정보 없음")
            .value_counts()
            .rename_axis("company_type")
            .reset_index(name="company_count")
        )
        type_chart = go.Figure(
            data=[
                go.Pie(
                    labels=type_summary["company_type"],
                    values=type_summary["company_count"],
                    hole=0.55,
                    textinfo="label+percent",
                    hovertemplate="%{label}<br>사업장 수: %{value:,}곳<extra></extra>",
                )
            ]
        )
        type_chart.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(type_chart, width="stretch")

    st.subheader("가입자 규모별 사업장 수")
    member_bins = [0, 10, 50, 100, 500, 1_000, 5_000, float("inf")]
    member_labels = ["1~10명", "11~50명", "51~100명", "101~500명", "501~1천명", "1천~5천명", "5천명 초과"]
    filtered_data["member_range"] = pd.cut(
        filtered_data["member_count"],
        bins=member_bins,
        labels=member_labels,
        include_lowest=True,
    )
    size_summary = (
        filtered_data["member_range"]
        .value_counts(sort=False)
        .rename_axis("member_range")
        .reset_index(name="company_count")
    )
    size_chart = px.bar(
        size_summary,
        x="member_range",
        y="company_count",
        labels={"member_range": "가입자 규모", "company_count": "사업장 수"},
        text="company_count",
        template="plotly_white",
    )
    size_chart.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
    size_chart.update_layout(
        xaxis_title="가입자 규모",
        yaxis_title="사업장 수",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(size_chart, width="stretch")

    st.subheader("가입자 수가 많은 사업장")
    display_columns = [
        column
        for column in ("company_name", "industry", "company_type", "sido", "member_count")
        if column in filtered_data.columns
    ]
    st.dataframe(
        filtered_data.sort_values("member_count", ascending=False)[display_columns].head(100),
        width="stretch",
        hide_index=True,
    )


if __name__ == "__main__":
    main()
