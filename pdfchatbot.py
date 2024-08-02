import streamlit as st
import pdfplumber
import io
from openai import OpenAI

def app():
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = ""

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    st.title("설계안 도우미 챗봇 - 성호중 박범진")

    uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
    if uploaded_file is not None:
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

            st.session_state.knowledge_base = text
            st.write("PDF에서 추출된 내용이 지식 베이스로 저장되었습니다.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_query = st.text_input("질문을 입력하세요:")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        with st.spinner('AI가 답변을 생성 중입니다...'):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.chat_history,
                max_tokens=1024
            )
        
        st.session_state.chat_history.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        
        for message in st.session_state.chat_history[-2:]:  # 최근 사용자 및 AI 응답만 표시
            role = "user" if message['role'] == "user" else "assistant"
            with st.chat_message(role):
                st.markdown(message['content'])
