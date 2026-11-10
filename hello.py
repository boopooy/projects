from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st


st.title("인사 앱")

name = st.text_input("이름을 입력하세요")

if name:
    st.write(f"안녕하세요, {name}님! 만나서 반가워요.")

if st.button("현재 시간 보기"):
    current_time = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"현재 시간: {current_time}")

if st.button("응원 메시지 받기"):
    st.write("오늘도 화이팅이에요! 당신은 할 수 있어요!")