"""Landing page for the Designer Tools Streamlit app."""

import streamlit as st


st.set_page_config(page_title="Designer Tools", page_icon="🎨", layout="wide")

st.title("🎨 Designer Tools")
st.caption("색상 선택과 이미지 분석을 한곳에서 편리하게 사용할 수 있어요.")

apps = [
    {
        "title": "RGB Color Picker",
        "description": "RGB 슬라이더로 색상을 선택하고 기본색·보조색·배경색 테마를 확인하세요.",
        "icon": "🎨",
        "page": "01_color_picker.py",
        "accent": "#6C5CE7",
    },
    {
        "title": "Image Color Extractor",
        "description": "이미지의 주요 색상 5개를 추출해 작업용 컬러 테마를 만드세요.",
        "icon": "🖼️",
        "page": "02_image_color.py",
        "accent": "#00B894",
    },
    {
        "title": "Image Filter Studio",
        "description": "이미지에 흑백, 세피아, 블러, 대비 강화 등 필터를 적용하고 다운로드하세요.",
        "icon": "🧙",
        "page": "03_image_filter.py",
        "accent": "#E17055",
    },
]

columns = st.columns(3)
for column, app in zip(columns, apps):
    with column:
        st.markdown(
            f"""
            <div style="
                border: 1px solid #e6e6e6;
                border-radius: 18px;
                padding: 24px;
                height: 100%;
                background: linear-gradient(145deg, #ffffff, #fafafa);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
            ">
                <div style="font-size: 42px;">{app["icon"]}</div>
                <h2 style="margin-top: 16px;">{app["title"]}</h2>
                <p style="color: #666; min-height: 70px;">{app["description"]}</p>
                <div style="height: 5px; background: {app["accent"]}; border-radius: 10px; margin-bottom: 18px;"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "도구 열기",
            key=f"open_{app['page']}",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page(f"pages/{app['page']}")

st.divider()
st.caption("Streamlit 기반 디자인 도구 · 이미지 처리는 브라우저에서 수행됩니다.")
