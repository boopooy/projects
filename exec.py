import streamlit as st

st.set_page_config(
    page_title="자기소개 앱",
    page_icon="👋",
    layout="centered"
)

# 스타일
st.markdown("""
<style>
    .intro-box {
        background-color: #f0f2f6;
        padding: 24px;
        border-radius: 12px;
        border-left: 5px solid #FF4B4B;
        font-size: 18px;
        margin-top: 20px;
    }
    h1 {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("👋 자기소개 앱")
st.write("이름, 직업, 취미를 입력하고 소개를 확인해보세요!")

st.divider()

# 입력 폼
with st.form("intro_form"):
    name = st.text_input("이름", placeholder="예: 김철수")
    job = st.text_input("직업", placeholder="예: 개발자, 디자이너, 학생")
    hobby = st.text_input("취미", placeholder="예: 독서, 게임, 등산")
    
    submitted = st.form_submit_button("소개 보기", use_container_width=True, type="primary")

# 출력
if submitted:
    if not name or not job or not hobby:
        st.warning("이름, 직업, 취미를 모두 입력해주세요!")
    else:
        st.balloons()
        st.markdown(f"""
        <div class="intro-box">
            저는 <b>{job}</b>으로 일하는 <b>{name}</b>입니다.<br>
            취미는 <b>{hobby}</b>예요.
        </div>
        """, unsafe_allow_html=True)
else:
    # 초기 안내
    st.info("위 정보를 입력하고 '소개 보기' 버튼을 눌러주세요.")

# 푸터
st.divider()
st.caption("Made with Streamlit")
