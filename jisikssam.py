import streamlit as st
from openai import OpenAI
import json

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

# GPT의 스트림 데이터를 처리하는 함수
def stream_gpt_response(prompt):
    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    return response  # 스트리밍 객체를 그대로 반환

def handle_button_click(button_type, student_input):
    st.session_state.design_messages.append({"role": "user", "content": f"{button_type}: {student_input}"})

    prompt = f"{button_type}로 입력된 내용에 대해 답변해줘: {student_input}"
    
    with st.spinner(f"{button_type}에 대한 응답 생성 중..."):
        try:
            # 스트리밍 객체를 가져와서 st.write_stream을 통해 출력
            stream = stream_gpt_response(prompt)
            response = st.write_stream(stream)  # 여기서 GPT의 응답이 실시간으로 출력됩니다.
            st.session_state.design_messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"오류 발생: {e}")

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
                try:
                    stream = stream_gpt_response(prompt)
                    response = st.write_stream(stream)  # 스트리밍된 데이터를 실시간으로 출력
                    st.session_state.design_messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"오류 발생: {e}")

        if st.session_state.get("question_generated"):
            for message in st.session_state.design_messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

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

if __name__ == "__main__":
    app()
