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

    user_query = st.text_input("질문을 입력하세요:", key="query_input")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history],
            max_tokens=1024
        )
        
        st.write(response)

        # response_text를 response.choices[0].text로 수정
        response_text = response.choices[0].text
        st.session_state.chat_history.append({"role": "assistant", "content": response_text})

        # 입력 필드를 비우기
        st.session_state["query_input"] = ""

    # 메시지 출력
    for message in st.session_state.chat_history:
        role = "user" if message['role'] == "user" else "assistant"
        if role == "user":
            st.info(message["content"])
        else:
            st.success(message["content"])
