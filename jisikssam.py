import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 계정 데이터 로드 함수
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 계정 데이터 저장 함수
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)

def app():
    st.title("성호중 박범진")

    # 로그인 상태를 체크하기 위한 세션 상태 변수
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")
        
        # 기존 코드 계속...

    else:
        # 이메일과 비밀번호 입력
        email = st.text_input("이메일을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")

        # 여기에서 load_accounts 함수가 사용됩니다.
        accounts = load_accounts()

        # 로그인 처리
        if st.button("로그인"):
            if email in accounts and accounts[email] == password:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email
                st.experimental_rerun()  # 로그인 후 화면 새로고침
            else:
                st.error("이메일 또는 비밀번호가 일치하지 않습니다.")

        # 계정 등록
        if st.button("계정 등록"):
            if email in accounts:
                st.error("이미 존재하는 이메일입니다.")
            else:
                accounts[email] = password
                save_accounts(accounts)
                st.success("계정이 성공적으로 등록되었습니다.")

if __name__ == "__main__":
    app()
