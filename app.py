import streamlit as st
import listen
import integral
import integraledit  # integraledit 모듈 불러오기
import pdfchatbot

st.set_page_config(
    page_title="Multi App",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = {
    "듣기평가 음원 만들기": listen,
    "Integral": integral,
    "적분 계산기": integraledit,  # 새로운 페이지 추가
    "PDF 챗봇": pdfchatbot
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]
page.app()  # 선택된 페이지의 app 함수 호출
