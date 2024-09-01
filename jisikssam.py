import streamlit as st
import json
from datetime import datetime

def app():  # 함수로 감싸기
    # 데이터 로드
    try:
        with open("accounts.json", "r") as file:
            accounts = json.load(file)
    except FileNotFoundError:
        accounts = {}

    # 계정 및 비밀번호 입력
    username = st.text_input("계정을 입력하세요:")
    password = st.text_input("비밀번호를 입력하세요", type="password")

    # 로그인 처리
    if st.button("로그인"):
        if username in accounts and accounts[username] == password:
            st.write(f"{username}님, 환영합니다!")

            # 데이터 로드
            try:
                with open("data.json", "r") as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}

            # 계정 데이터 표시 및 추가
            user_data = data.get(username, [])
            if user_data:
                st.write(f"{username}님의 데이터 기록:")
                for entry in user_data:
                    st.write(f"- {entry['timestamp']}")
            else:
                st.write("아직 저장된 데이터가 없습니다.")
            
            # 데이터 추가
            if st.button("데이터 추가"):
                if username not in data:
                    data[username] = []
                data[username].append({"timestamp": str(datetime.now())})

                # 데이터 저장
                with open("data.json", "w") as file:
                    json.dump(data, file)
                
                st.write("데이터가 추가되었습니다.")
        else:
            st.write("계정 또는 비밀번호가 일치하지 않습니다.")

    # 계정 등록
    if st.button("계정 등록"):
        if username in accounts:
            st.write("이미 존재하는 계정입니다.")
        else:
            accounts[username] = password
            with open("accounts.json", "w") as file:
                json.dump(accounts, file)
            st.write("계정이 성공적으로 등록되었습니다.")
