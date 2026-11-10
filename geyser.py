import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from geyser_analysis import filter_data, fit_linear_regression

st.set_page_config(
    page_title="Old Faithful 대시보드",
    page_icon="🌋",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    return sns.load_dataset("geyser")


try:
    df = load_data()
except (OSError, ValueError) as exc:
    st.error(f"간헐천 데이터를 불러오지 못했습니다. 네트워크 연결을 확인해 주세요. ({exc})")
    st.stop()

required_columns = {"duration", "waiting", "kind"}
missing_columns = required_columns.difference(df.columns)
if missing_columns:
    st.error(f"데이터에 필요한 열이 없습니다: {', '.join(sorted(missing_columns))}")
    st.stop()

if df.empty or df[list(required_columns)].isna().any().any():
    st.error("분석할 데이터가 비어 있거나 필수 항목에 결측치가 있습니다.")
    st.stop()

st.sidebar.title("🌋 Old Faithful")
st.sidebar.caption("옐로스톤 간헐천 분출 데이터 탐색")
st.sidebar.subheader("데이터 필터")

kinds = sorted(df["kind"].unique().tolist())
selected_kinds = st.sidebar.multiselect(
    "분출 유형",
    options=kinds,
    default=kinds,
)
duration_bounds = (
    float(df["duration"].min()),
    float(df["duration"].max()),
)
duration_range = st.sidebar.slider(
    "분출 지속 시간 (분)",
    min_value=duration_bounds[0],
    max_value=duration_bounds[1],
    value=duration_bounds,
    step=0.1,
)
waiting_bounds = (
    float(df["waiting"].min()),
    float(df["waiting"].max()),
)
waiting_range = st.sidebar.slider(
    "다음 분출까지 대기 시간 (분)",
    min_value=waiting_bounds[0],
    max_value=waiting_bounds[1],
    value=waiting_bounds,
    step=1.0,
)

filtered_df = filter_data(
    df,
    selected_kinds,
    duration_range,
    waiting_range,
)

st.title("Old Faithful 간헐천 데이터 대시보드")
st.caption(
    "분출 지속 시간과 다음 분출까지의 대기 시간을 살펴보고, "
    "필터 결과를 바탕으로 간단한 선형 회귀 예측을 확인합니다."
)

metric_columns = st.columns(4)
metric_columns[0].metric("관측 횟수", f"{len(filtered_df):,}")
if filtered_df.empty:
    metric_columns[1].metric("평균 분출 시간", "—")
    metric_columns[2].metric("평균 대기 시간", "—")
    metric_columns[3].metric("분출 유형 수", "0")
else:
    metric_columns[1].metric(
        "평균 분출 시간",
        f"{filtered_df['duration'].mean():.2f}분",
    )
    metric_columns[2].metric(
        "평균 대기 시간",
        f"{filtered_df['waiting'].mean():.1f}분",
    )
    metric_columns[3].metric("분출 유형 수", str(filtered_df["kind"].nunique()))

st.divider()

if filtered_df.empty:
    st.info("선택한 조건에 해당하는 데이터가 없습니다. 사이드바 필터를 조정해 주세요.")
else:
    st.subheader("분출 데이터 탐색")
    scatter_tab, distribution_tab = st.tabs(["대기 시간과 분출 시간", "분포 비교"])

    with scatter_tab:
        scatter = px.scatter(
            filtered_df,
            x="waiting",
            y="duration",
            color="kind",
            labels={
                "waiting": "다음 분출까지 대기 시간 (분)",
                "duration": "분출 지속 시간 (분)",
                "kind": "분출 유형",
            },
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"waiting": ":.1f", "duration": ":.2f"},
        )
        scatter.update_layout(
            legend_title_text="분출 유형",
            margin=dict(l=10, r=10, t=25, b=10),
        )
        st.plotly_chart(scatter, width="stretch")

    with distribution_tab:
        duration_chart = px.histogram(
            filtered_df,
            x="duration",
            color="kind",
            barmode="overlay",
            opacity=0.7,
            labels={
                "duration": "분출 지속 시간 (분)",
                "count": "관측 수",
                "kind": "분출 유형",
            },
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        duration_chart.update_layout(
            legend_title_text="분출 유형",
            margin=dict(l=10, r=10, t=25, b=10),
        )
        st.plotly_chart(duration_chart, width="stretch")

    st.subheader("필터링된 관측 데이터")
    display_df = filtered_df.rename(
        columns={
            "duration": "분출 지속 시간 (분)",
            "waiting": "다음 분출까지 대기 시간 (분)",
            "kind": "분출 유형",
        }
    )
    st.dataframe(display_df, width="stretch", hide_index=True)
    st.download_button(
        "필터 결과 CSV 다운로드",
        data=display_df.to_csv(index=False).encode("utf-8-sig"),
        file_name="geyser_filtered.csv",
        mime="text/csv",
        width="stretch",
    )

    st.divider()
    st.subheader("대기 시간으로 분출 시간 예측")
    if filtered_df["waiting"].nunique() < 2:
        st.info("회귀 예측을 하려면 필터 결과에 서로 다른 대기 시간이 두 개 이상 필요합니다.")
    else:
        slope, intercept, r_squared = fit_linear_regression(filtered_df)
        minimum_waiting = float(filtered_df["waiting"].min())
        maximum_waiting = float(filtered_df["waiting"].max())

        prediction_columns = st.columns([1, 2])
        with prediction_columns[0]:
            input_waiting = st.slider(
                "예측할 대기 시간 (분)",
                min_value=minimum_waiting,
                max_value=maximum_waiting,
                value=float(filtered_df["waiting"].mean()),
                step=0.5,
            )
            predicted_duration = slope * input_waiting + intercept
            st.metric("예상 분출 지속 시간", f"{predicted_duration:.2f}분")
            st.metric("모델 설명력 (R²)", f"{r_squared:.3f}")

        with prediction_columns[1]:
            prediction_chart = px.scatter(
                filtered_df,
                x="waiting",
                y="duration",
                color="kind",
                labels={
                    "waiting": "다음 분출까지 대기 시간 (분)",
                    "duration": "분출 지속 시간 (분)",
                    "kind": "분출 유형",
                },
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            line_x = [minimum_waiting, maximum_waiting]
            prediction_chart.add_trace(
                go.Scatter(
                    x=line_x,
                    y=[slope * value + intercept for value in line_x],
                    mode="lines",
                    name="선형 회귀 추세선",
                    line=dict(color="#EF553B", width=3),
                )
            )
            prediction_chart.add_trace(
                go.Scatter(
                    x=[input_waiting],
                    y=[predicted_duration],
                    mode="markers",
                    name="선택한 예측값",
                    marker=dict(color="#222222", size=12, symbol="diamond"),
                )
            )
            prediction_chart.update_layout(
                legend_title_text="분출 유형",
                margin=dict(l=10, r=10, t=25, b=10),
            )
            st.plotly_chart(prediction_chart, width="stretch")

        st.caption(
            f"선형 회귀식: 분출 시간 = {slope:.4f} × 대기 시간 + ({intercept:.4f}). "
            "예측은 선택한 필터 결과로 계산됩니다."
        )
