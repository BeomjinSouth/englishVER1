import streamlit as st
import json
from datetime import datetime
import openai  # GPT API 사용

# 이메일 전송 라이브러리
import smtplib
from email.mime.text import MIMEText

# GPT API 설정
openai.api_key = 'YOUR_OPENAI_API_KEY'

# 데이터 로드
try:
    with open("accounts.json", "r") as file:
        accounts = json.load(file)
except FileNotFoundError:
    accounts = {}

# 이메일과 비밀번호 입력 및 로그인 처리
email = st.text_input("이메일을 입력하세요:")
password = st.text_input("비밀번호를 입력하세요", type="password")

if st.button("로그인"):
    if email in accounts and accounts[email] == password:
        st.success(f"{email}님, 환영합니다!")

        # 과목, 주제, 문항 설정
        subject = st.selectbox("과목을 선택하세요", ["수학", "과학", "영어", "역사"])
        topic = st.text_input("주제를 입력하세요")
        num_questions = st.number_input("문항 개수를 입력하세요", min_value=1, max_value=10)
        difficulty = st.selectbox("난이도를 선택하세요", ["쉬움", "중간", "어려움"])
        question_type = st.selectbox("문항 유형을 선택하세요", ["논술형", "객관식"])

        if st.button("생성하기"):
            # GPT API를 활용해 문항 생성
            prompt = f"Create {num_questions} {difficulty} level questions on {topic} for {subject} subject. Format: {question_type}."
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500
            )
            questions = response.choices[0].text.strip()
            st.write("생성된 문항:")
            st.write(questions)

            # 채팅 형식의 문항 풀이
            user_responses = []
            for i, question in enumerate(questions.split('\n'), start=1):
                response = st.text_area(f"Q{i}: {question}", "")
                user_responses.append(response)

            if st.button("응답 완료"):
                # 응답을 GPT로 평가
                evaluation_prompt = f"Evaluate these responses: {user_responses} based on the questions {questions}."
                evaluation_response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=evaluation_prompt,
                    max_tokens=500
                )
                evaluation = evaluation_response.choices[0].text.strip()

                # 학습 기록 저장
                try:
                    with open("learning_data.json", "r") as file:
                        learning_data = json.load(file)
                except FileNotFoundError:
                    learning_data = {}

                if email not in learning_data:
                    learning_data[email] = []
                
                learning_data[email].append({
                    "timestamp": str(datetime.now()),
                    "subject": subject,
                    "topic": topic,
                    "questions": questions,
                    "responses": user_responses,
                    "evaluation": evaluation
                })

                with open("learning_data.json", "w") as file:
                    json.dump(learning_data, file)

                # 이메일로 평가 결과 전송
                msg = MIMEText(evaluation)
                msg['Subject'] = f"{subject} 주제 {topic}에 대한 학습 평가"
                msg['From'] = 'your_email@example.com'
                msg['To'] = email

                # Gmail을 사용한 예시 (SMTP 설정 필요)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login('your_email@example.com', 'your_email_password')
                    server.send_message(msg)

                st.success("평가가 완료되었으며, 이메일로 전송되었습니다.")

    else:
        st.error("이메일 또는 비밀번호가 일치하지 않습니다.")

# 계정 등록
if st.button("계정 등록"):
    if email in accounts:
        st.error("이미 존재하는 이메일입니다.")
    else:
        accounts[email] = password
        with open("accounts.json", "w") as file:
            json.dump(accounts, file)
        st.success("계정이 성공적으로 등록되었습니다.")
