import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 계정 데이터를 로드하는 함수
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 계정 데이터를 저장하는 함수
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)

# 학습 데이터를 로드하는 함수
def load_learning_data():
    try:
        with open("learning_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 학습 데이터를 저장하는 함수
def save_learning_data(learning_data):
    with open("learning_data.json", "w") as file:
        json.dump(learning_data, file)

# 이메일을 전송하는 함수
def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@gmail.com"  # 실제 Gmail 주소로 변경하세요.
    smtp_password = st.secrets["EMAIL_PASSWORD"]  # 비밀번호는 secrets에서 불러옵니다.

    msg = MIMEMultipart()
    msg['From'] = smtp_user  # 보내는 사람의 이메일 주소
    msg['To'] = to_email  # 받는 사람의 이메일 주소
    msg['Subject'] = subject  # 이메일 제목

    body = MIMEText(body, 'plain')
    msg.attach(body)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # TLS 시작
        server.login(smtp_user, smtp_password)  # SMTP 서버에 로그인
        server.sendmail(smtp_user, to_email, msg.as_string())  # 이메일 전송

# GPT의 스트림 데이터를 처리하는 함수
def stream_gpt_response(prompt):
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    full_response = ""
    for chunk in response:
        if "choices" in chunk:
            if chunk["choices"][0].get("delta", {}).get("content"):
                content = chunk["choices"][0]["delta"]["content"]
                full_response += content
                yield content

    st.session_state["last_gpt_response"] = full_response

# 메인 애플리케이션 함수
def app():
    st.title("학습 도우미 시스템")

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")

        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o-mini"
        if "design_messages" not in st.session_state:
            st.session_state.design_messages = []
        if "question_generated" not in st.session_state:
            st.session_state["question_generated"] = False

        main_category = st.selectbox("대분류를 선택하세요", ["영어", "수학", "과학"])
        sub_category = st.selectbox("소분류를 선택하세요", ["문법", "독해", "어휘"])
        topic = st.selectbox("주제를 선택하세요", ["수동태", "현재완료", "관계대명사"])
        num_questions = st.number_input('문항 개수를 선택하세요', min_value=1, max_value=10, value=3)
        difficulty = st.selectbox('난이도를 선택하세요', ['쉬움', '보통', '어려움'])
        question_type = st.selectbox('문항 유형을 선택하세요', ['논술형', '객관식'])

        if st.button('생성하기'):
            st.session_state.design_messages = []
            prompt = f"{main_category} - {sub_category}: '{topic}' 주제의 {num_questions}개의 문항을 생성해줘. 난이도는 {difficulty}이고, 문항 유형은 {question_type}이다."
            st.session_state.design_messages.append({"role": "user", "content": prompt})
            st.session_state["question_generated"] = True

            # GPT의 응답을 스트리밍으로 출력
            with st.spinner("문항 생성 중..."):
                st.session_state["last_gpt_response"] = ""
                for word in stream_gpt_response(prompt):
                    st.write_stream(word)

            # 마지막 GPT 응답을 화면에 표시
            st.session_state.design_messages.append({"role": "assistant", "content": st.session_state["last_gpt_response"]})

        if st.session_state.get("question_generated"):
            for message in st.session_state.design_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # 입력칸과 버튼을 나란히 배치
            col1, col2 = st.columns([3, 1])
            with col1:
                student_input = st.text_area('여기에 질문이나 답변을 입력하세요', key="student_input")

            with col2:
                if st.button('질문하기'):
                    handle_button_click("질문하기", student_input)

                if st.button('얘기하기'):
                    handle_button_click("얘기하기", student_input)

                if st.button('평가 요청'):
                    handle_button_click("평가 요청", student_input)

    else:
        st.header("로그인 또는 계정 생성")

        email = st.text_input("이메일을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")

        accounts = load_accounts()

        if st.button("로그인"):
            if email in accounts and accounts[email] == password:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email
                st.experimental_set_query_params(logged_in="true")
            else:
                st.error("이메일 또는 비밀번호가 일치하지 않습니다.")

        if st.button("계정 등록"):
            if email in accounts:
                st.error("이미 존재하는 이메일입니다.")
            else:
                accounts[email] = password
                save_accounts(accounts)
                st.success("계정이 성공적으로 등록되었습니다.")

def handle_button_click(button_type, student_input):
    st.session_state.design_messages.append({"role": "user", "content": f"{button_type}: {student_input}"})

    prompt = f"{button_type}로 입력된 내용에 대해 답변해줘: {student_input}"
    
    with st.spinner(f"{button_type}에 대한 응답 생성 중..."):
        st.session_state["last_gpt_response"] = ""
        for word in stream_gpt_response(prompt):
            st.write_stream(word)
    
    st.session_state.design_messages.append({"role": "assistant", "content": st.session_state["last_gpt_response"]})

if __name__ == "__main__":
    app()
