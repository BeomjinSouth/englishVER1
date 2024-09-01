import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# OpenAI API 키 설정 (secrets에서 가져오기)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 이메일 전송 함수 설정
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login('your_email@example.com', 'your_email_password')
        server.send_message(msg)

# 계정 데이터 로드
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 계정 데이터 저장
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)

# 학습 데이터 로드
def load_learning_data():
    try:
        with open("learning_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 학습 데이터 저장
def save_learning_data(learning_data):
    with open("learning_data.json", "w") as file:
        json.dump(learning_data, file)

def app():  # 이 함수가 app.py에서 호출됩니다.
    st.title("지식쌤")

    # 로그인 상태를 체크하기 위한 세션 상태 변수
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")

        # 과목 선택, 주제 입력, 문항 개수, 난이도, 문항 유형 설정
        subject = st.selectbox("과목을 선택하세요", ["수학", "과학", "영어", "역사"])
        topic = st.text_input("주제를 입력하세요")
        num_questions = st.number_input("문항 개수를 입력하세요", min_value=1, max_value=10)
        difficulty = st.selectbox("난이도를 선택하세요", ["쉬움", "중간", "어려움"])
        question_type = st.selectbox("문항 유형을 선택하세요", ["논술형", "객관식"])

        if st.button("생성하기"):
            # GPT API를 통해 문제 생성
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Create {num_questions} {difficulty} level {question_type} questions on the topic of {topic} for {subject}."}
            ]

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=False,
            )
            
            questions = response['choices'][0]['message']['content'].strip()
            st.write("생성된 문항:")
            st.write(questions)

            # 사용자가 문항에 응답을 입력할 수 있는 텍스트 필드
            user_responses = []
            for i, question in enumerate(questions.split('\n'), start=1):
                response = st.text_area(f"Q{i}: {question}", "")
                user_responses.append(response)

            if st.button("응답 완료"):
                # 응답 평가
                evaluation_prompt = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Evaluate these responses: {user_responses} based on the questions {questions}."}
                ]

                evaluation_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=evaluation_prompt,
                    stream=False,
                )
                
                evaluation = evaluation_response['choices'][0]['message']['content'].strip()

                # 학습 데이터 저장
                learning_data = load_learning_data()
                email = st.session_state['email']
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
                save_learning_data(learning_data)

                # 평가 결과 이메일로 전송
                send_email(email, f"{subject} 주제 {topic}에 대한 학습 평가", evaluation)
                st.success("평가가 완료되었으며, 이메일로 전송되었습니다.")

    else:
        # 이메일과 비밀번호 입력
        email = st.text_input("이메일을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")

        accounts = load_accounts()

        # 로그인 처리
        if st.button("로그인"):
            if email in accounts and accounts[email] == password:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email
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
