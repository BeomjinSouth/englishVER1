import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

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

def app():
    st.title("성호중 박범진")

    # 로그인 상태를 체크하기 위한 세션 상태 변수
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")

        # 사용자 세션 상태 초기화
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o-mini"
        if "design_messages" not in st.session_state:
            st.session_state.design_messages = []

        # 사용자 입력받기
        subject = st.selectbox('과목을 선택하세요', ['수학', '과학', '역사'])
        topic = st.text_input('원하는 주제를 입력하세요')
        num_questions = st.number_input('문항 개수를 선택하세요', min_value=1, max_value=10, value=3)
        difficulty = st.selectbox('난이도를 선택하세요', ['쉬움', '보통', '어려움'])
        question_type = st.selectbox('문항 유형을 선택하세요', ['논술형', '객관식'])

        # 문항 생성 요청
        if st.button('생성하기'):
            prompt = f"{subject} 과목에서 '{topic}' 주제의 {num_questions}개의 문항을 생성해줘. 난이도는 {difficulty}이고, 문항 유형은 {question_type}이다."
            st.session_state.design_messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            # GPT 응답 생성 및 출력
            with st.chat_message("assistant"):
                try:
                    response_content = ""
                    stream = openai.ChatCompletion.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.design_messages
                        ],
                        stream=True,
                    )

                    for chunk in stream:
                        content = chunk.choices[0].delta.get('content', '')
                        response_content += content
                        st.write(content)

                    st.session_state.design_messages.append({"role": "assistant", "content": response_content})
                
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

        # 학생의 답변과 평가 주고받기
        if st.button('응답 완료'):
            st.session_state['response_complete'] = True

        if st.session_state.get('response_complete'):
            student_answer = st.text_area('여기에 답변을 입력하세요')
            if st.button('제출'):
                # 학생의 답변을 세션에 저장
                st.session_state.design_messages.append({"role": "user", "content": student_answer})

                with st.chat_message("user"):
                    st.markdown(student_answer)

                # 평가 요청 및 처리
                with st.chat_message("assistant"):
                    evaluation_prompt = f"학생의 답변을 평가해주세요: {student_answer}"
                    st.session_state.design_messages.append({"role": "user", "content": evaluation_prompt})

                    response_content = ""
                    stream = openai.ChatCompletion.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.design_messages
                        ],
                        stream=True,
                    )

                    for chunk in stream:
                        content = chunk.choices[0].delta.get('content', '')
                        response_content += content
                        st.write(content)

                    st.session_state.design_messages.append({"role": "assistant", "content": response_content})

                # 이메일 발송 (학생의 학습 결과 평가)
                send_email(st.session_state['email'], response_content)
                st.success("평가가 완료되었으며 이메일로 전송되었습니다.")

                # 학습 데이터 저장
                learning_data = load_learning_data()
                email = st.session_state['email']
                if email not in learning_data:
                    learning_data[email] = []

                learning_data[email].append({
                    "timestamp": str(datetime.now()),
                    "subject": subject,
                    "topic": topic,
                    "questions": response_content,
                    "responses": student_answer,
                    "evaluation": response_content
                })
                save_learning_data(learning_data)

                # 상태 리셋
                st.session_state['response_complete'] = False

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

def send_email(to_email, evaluation_content):
    # SMTP 서버 설정 (이 예제에서는 Gmail을 사용)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@example.com"
    smtp_password = st.secrets["EMAIL_PASSWORD"]

    # 이메일 메시지 작성
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = "GPT 학습 평가 결과"

    body = MIMEText(evaluation_content, 'plain')
    msg.attach(body)

    # 이메일 전송
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())

if __name__ == "__main__":
    app()
