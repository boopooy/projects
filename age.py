from datetime import date

import streamlit as st


current_year = date.today().year

st.title("나이 계산기")
birth_year = st.number_input(
    "태어난 연도를 입력하세요",
    min_value=1900,
    max_value=current_year,
    step=1,
    value=2000,
)

if st.button("나이 계산"):
    age = current_year - int(birth_year)
    st.write(f"올해 {age}살이에요!")
