from datetime import date
import os

import pandas as pd
import streamlit as st


DIARY_FILE = "diary.csv"
WEATHER_OPTIONS = ["맑음", "흐림", "비", "눈", "바람"]
COLUMNS = ["날짜", "제목", "내용", "날씨"]


st.title("📔 나의 일기장")

title = st.text_input("제목")
content = st.text_area("내용", height=150)
weather = st.selectbox("오늘의 날씨", WEATHER_OPTIONS)

if st.button("저장"):
    entry = pd.DataFrame(
        [[date.today().strftime("%Y-%m-%d"), title, content, weather]],
        columns=COLUMNS,
    )
    entry.to_csv(
        DIARY_FILE,
        mode="a",
        header=not os.path.exists(DIARY_FILE),
        index=False,
        encoding="utf-8-sig",
    )
    st.success("일기가 저장되었어요!")

if os.path.exists(DIARY_FILE):
    diary = pd.read_csv(DIARY_FILE, encoding="utf-8-sig")
    st.dataframe(diary)
else:
    st.write("아직 작성된 일기가 없어요.")