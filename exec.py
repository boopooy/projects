import streamlit as st

st.title("자기소개")

name = st.text_input("이름")
job = st.text_input("직업")
hobby = st.text_input("취미")

if st.button("소개 보기"):
    st.write(f"저는 {job}으로 일하는 {name}입니다. 취미는 {hobby}예요.")
