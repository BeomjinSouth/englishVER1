import streamlit as st
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def app():
    st.title("설계안 도우미 챗봇 - 성호중 박범진")

    # 사용자 세션 상태 초기화
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"
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
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.design_messages
                ],
                stream=True,
            )

            response_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.get('content', '')
                response_content += content
                st.write(content)

            st.session_state.design_messages.append({"role": "assistant", "content": response_content})

    # 학생의 답변과 평가 주고받기
    if '응답 완료' in st.session_state:
        student_answer = st.text_area('여기에 답변을 입력하세요')
        if st.button('제출'):
            st.session_state.design_messages.append({"role": "user", "content": student_answer})
            
            with st.chat_message("user"):
                st.markdown(student_answer)
            
            # 평가 요청 및 처리
            with st.chat_message("assistant"):
                evaluation_prompt = f"학생의 답변을 평가해주세요: {student_answer}"
                st.session_state.design_messages.append({"role": "user", "content": evaluation_prompt})

                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.design_messages
                    ],
                    stream=True,
                )

                evaluation_content = ""
                for chunk in stream:
                    content = chunk.choices[0].delta.get('content', '')
                    evaluation_content += content
                    st.write(content)

                st.session_state.design_messages.append({"role": "assistant", "content": evaluation_content})

            # 이메일 발송 (학생의 학습 결과 평가)
            send_email("student_email@example.com", evaluation_content)
            st.success("평가가 완료되었으며 이메일로 전송되었습니다.")

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

def update_learning_record(user_email, new_evaluation):
    # 기존 학습 기록 가져오기 (이 예제에서는 간단하게 세션 상태에 저장)
    if "learning_records" not in st.session_state:
        st.session_state["learning_records"] = {}

    if user_email not in st.session_state["learning_records"]:
        st.session_state["learning_records"][user_email] = []

    # 새 평가 기록 추가
    st.session_state["learning_records"][user_email].append(new_evaluation)

    # 간단한 예시: 과거의 평가와 비교하여 개선되었는지 분석
    past_records = st.session_state["learning_records"][user_email]
    if len(past_records) > 1:
        if past_records[-1] > past_records[-2]:
            st.write("이전보다 더 좋아졌습니다.")
        else:
            st.write("이전과 비슷하거나 조금 나빠졌습니다. 이런 부분에 대해 보완이 필요합니다.")
    else:
        st.write("첫 평가입니다. 계속 학습하여 개선해 나가세요.")
