import listen
import integral
import streamlit as st

# 여기서 필요한 추가 설정이나 Streamlit app 정의
st.set_page_config(
    page_title="Multi App",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 페이지 옵션 설정
PAGES = {
    "듣기평가 음원 만들기": listen,
    "Integral": integral,
}

# 사이드바에 페이지 옵션 추가
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# 선택된 페이지 로드
page = PAGES[selection]
page.app()
