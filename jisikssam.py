import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정 (Streamlit secrets를 통해 API 키를 불러옵니다)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 계정 데이터 로드 함수 - 계정 정보를 저장한 JSON 파일을 불러옵니다
def load_accounts():
    try:
        with open("accounts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 계정 데이터 저장 함수 - 새로 생성된 계정 정보를 JSON 파일에 저장합니다
def save_accounts(accounts):
    with open("accounts.json", "w") as file:
        json.dump(accounts, file)

# 학습 데이터 로드 함수 - 사용자의 학습 기록을 불러옵니다
def load_learning_data():
    try:
        with open("learning_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# 학습 데이터 저장 함수 - 사용자의 학습 기록을 JSON 파일에 저장합니다
def save_learning_data(learning_data):
    with open("learning_data.json", "w") as file:
        json.dump(learning_data, file)

# 이메일 전송 함수 - 사용자의 학습 결과를 이메일로 전송합니다
def send_email(to_email, evaluation_content):
    # SMTP 서버 설정 (이 예제에서는 Gmail을 사용)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "your_email@gmail.com"  # 본인의 Gmail 주소로 변경
    smtp_password = st.secrets["EMAIL_PASSWORD"]  # 비밀번호는 secrets에서 불러옵니다.

    # 이메일 메시지 작성
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = "GPT 학습 평가 결과"

    body = MIMEText(evaluation_content, 'plain')
    msg.attach(body)

    # 이메일 전송 - SMTP 서버에 연결하여 이메일을 전송합니다
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # TLS (Transport Layer Security) 시작
        server.login(smtp_user, smtp_password)  # SMTP 서버에 로그인
        server.sendmail(smtp_user, to_email, msg.as_string())  # 이메일 전송

# 메인 애플리케이션 함수
def app():
    st.title("학습 도우미 시스템")

    # 로그인 상태를 체크하기 위한 세션 상태 변수 초기화
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # 사용자가 로그인 상태인지 확인하고 로그인 후 화면을 표시
    if st.session_state['logged_in']:
        st.success(f"{st.session_state['email']}님, 환영합니다!")

        # 세션 상태 초기화 - 처음 페이지 로드 시 필요
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o-mini"  # 사용할 OpenAI 모델 설정
        if "design_messages" not in st.session_state:
            st.session_state.design_messages = []  # 메시지 히스토리 초기화

        # 사용자 입력 받기 - 학습 과목, 주제, 문항 개수, 난이도, 문항 유형
        subject = st.selectbox('과목을 선택하세요', ['수학', '과학', '역사'])
        topic = st.text_input('원하는 주제를 입력하세요')
        num_questions = st.number_input('문항 개수를 선택하세요', min_value=1, max_value=10, value=3)
        difficulty = st.selectbox('난이도를 선택하세요', ['쉬움', '보통', '어려움'])
        question_type = st.selectbox('문항 유형을 선택하세요', ['논술형', '객관식'])

        # GPT API를 사용해 문항을 생성 요청
        if st.button('생성하기'):
            prompt = f"{subject} 과목에서 '{topic}' 주제의 {num_questions}개의 문항을 생성해줘. 난이도는 {difficulty}이고, 문항 유형은 {question_type}이다."
            st.session_state.design_messages.append({"role": "user", "content": prompt})

            # 사용자에게 프롬프트를 표시
            with st.chat_message("user"):
                st.markdown(prompt)

            # GPT 응답을 생성하여 출력
            with st.chat_message("assistant"):
                try:
                    response_content = ""
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.design_messages
                        ],
                        stream=True,
                    )

                    # 스트리밍으로 응답을 받아 화면에 출력
                    for chunk in stream:
                        if 'content' in chunk.choices[0].delta:
                            content = chunk.choices[0].delta['content']
                            response_content += content
                            st.write(content)  # GPT가 생성한 내용을 출력합니다.

                    # 응답 메시지를 세션 상태에 저장
                    st.session_state.design_messages.append({"role": "assistant", "content": response_content})

                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

            # GPT가 생성한 문제를 화면에 표시
            st.markdown("### 생성된 문제:")
            st.markdown(response_content)  # 생성된 문제를 화면에 표시합니다.

        # 학생의 답변 제출 및 평가
        if st.button('응답 완료'):
            st.session_state['response_complete'] = True

        if st.session_state.get('response_complete'):
            student_answer = st.text_area('여기에 답변을 입력하세요')
            if st.button('제출'):
                # 학생의 답변을 세션 상태에 저장
                st.session_state.design_messages.append({"role": "user", "content": student_answer})

                with st.chat_message("user"):
                    st.markdown(student_answer)

                # GPT에게 학생의 답변을 평가하도록 요청
                with st.chat_message("assistant"):
                    evaluation_prompt = f"학생의 답변을 평가해주세요: {student_answer}"
                    st.session_state.design_messages.append({"role": "user", "content": evaluation_prompt})

                    response_content = ""
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.design_messages
                        ],
                        stream=True,
                    )

                    for chunk in stream:
                        if 'content' in chunk.choices[0].delta:
                            content = chunk.choices[0].delta['content']
                            response_content += content
                            st.write(content)

                    st.session_state.design_messages.append({"role": "assistant", "content": response_content})

                # 평가 결과를 이메일로 전송
                send_email(st.session_state['email'], response_content)
                st.success("평가가 완료되었으며 이메일로 전송되었습니다.")

                # 학습 데이터를 저장
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
        # 로그인하지 않은 상태에서 로그인 및 계정 생성 화면 표시
        st.header("로그인 또는 계정 생성")

        email = st.text_input("이메일을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")

        accounts = load_accounts()

        # 로그인 처리
        if st.button("로그인"):
            if email in accounts and accounts[email] == password:
                st.session_state['logged_in'] = True
                st.session_state['email'] = email  # 세션 상태에 이메일 저장
                st.experimental_set_query_params(logged_in="true")
                st.experimental_rerun()  # 로그인 후 화면 갱신
            else:
                st.error("이메일 또는 비밀번호가 일치하지 않습니다.")

        # 계정 등록 처리
        if st.button("계정 등록"):
            if email in accounts:
                st.error("이미 존재하는 이메일입니다.")
            else:
                accounts[email] = password
                save_accounts(accounts)
                st.success("계정이 성공적으로 등록되었습니다.")

if __name__ == "__main__":
    app()
