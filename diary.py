import json
import os
from datetime import date

import pandas as pd
import streamlit as st


DIARY_FILE = "diary.csv"
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "author_name": "",
    "theme": "파랑",
    "last_viewed_date": None,
}
THEME_COLORS = {
    "파랑": "#2196F3",
    "초록": "#4CAF50",
    "보라": "#9C27B0",
    "주황": "#FF9800",
    "빨강": "#F44336",
}
DIARY_COLUMNS = ["날짜", "제목", "내용", "날씨", "작성자"]


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, encoding="utf-8") as settings_file:
            settings = json.load(settings_file)
        if not isinstance(settings, dict):
            raise ValueError(f"{SETTINGS_FILE} must contain a JSON object")
    except (OSError, UnicodeError, ValueError):
        st.warning("설정 파일이 손상되어 기본값으로 초기화했어요.")
        return DEFAULT_SETTINGS.copy()

    return {**DEFAULT_SETTINGS, **settings}


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
        json.dump(settings, settings_file, ensure_ascii=False, indent=2)


settings = load_settings()
previous_viewed_date = settings.get("last_viewed_date")
settings["last_viewed_date"] = date.today().isoformat()

with st.sidebar:
    with st.form("settings_form"):
        author_name = st.text_input("작성자 이름", value=settings.get("author_name", ""))
        if st.form_submit_button("저장"):
            settings["author_name"] = author_name
            save_settings(settings)
            st.success("이름이 저장되었습니다!")

    saved_theme = settings.get("theme", "파랑")
    theme_options = list(THEME_COLORS)
    theme_index = theme_options.index(saved_theme) if saved_theme in theme_options else 0
    selected_theme = st.selectbox("테마 색상", theme_options, index=theme_index)
    settings["theme"] = selected_theme

save_settings(settings)

st.markdown(
    f"""
    <div style="background-color: {THEME_COLORS[selected_theme]}; padding: 16px;
                border-radius: 8px; color: white; text-align: center;">
        오늘의 일기 테마: {selected_theme}
    </div>
    """,
    unsafe_allow_html=True,
)
st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", ["맑음", "흐림", "비", "눈", "바람"])

if st.button("일기 저장"):
    new_entry = pd.DataFrame(
        [
            {
                "날짜": date.today().isoformat(),
                "제목": title,
                "내용": content,
                "날씨": weather,
                "작성자": settings.get("author_name", ""),
            }
        ],
        columns=DIARY_COLUMNS,
    )

    if os.path.exists(DIARY_FILE):
        saved_entries = pd.read_csv(DIARY_FILE, encoding="utf-8-sig")
        diary = pd.concat([saved_entries, new_entry], ignore_index=True)
    else:
        diary = new_entry

    diary.to_csv(DIARY_FILE, index=False, encoding="utf-8-sig")
    st.success("일기가 저장되었습니다!")

st.subheader("저장된 일기")
if os.path.exists(DIARY_FILE):
    st.dataframe(pd.read_csv(DIARY_FILE, encoding="utf-8-sig"))
else:
    st.write("아직 작성된 일기가 없어요.")

if previous_viewed_date:
    st.write(f"마지막으로 일기를 확인한 날: {previous_viewed_date}")
else:
    st.write("처음 방문이에요! 일기를 써봐요 🌱")
