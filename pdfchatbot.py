import streamlit as st
import pdfplumber
import io
from openai import OpenAI

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])

# Streamlit 앱 구성
st.title("수업 설계 도우미 챗봇")

# PDF 파일 업로드와 처리
uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
if uploaded_file is not None:
    with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
        text = ''
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    st.session_state['knowledge_base'] = text
    st.write("PDF에서 추출된 내용이 지식 베이스로 저장되었습니다.")

# 사용자 입력 및 챗봇 응답 처리
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("질문을 입력하세요:")
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # OpenAI Chat Completion API 호출
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history] + [{"role": "system", "content": st.session_state.get('knowledge_base', '')}],
        max_tokens=1024
    )
    response_text = response.choices[0].text.strip()
    st.session_state.chat_history.append({"role": "assistant", "content": response_text})

    # 응답 출력
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.info(message["content"])
        else:
            st.success(message["content"])

    # 입력 필드 초기화
    st.session_state['user_input'] = ""
