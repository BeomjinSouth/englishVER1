import streamlit as st
from pathlib import Path
from openai import OpenAI
from collections import Counter
import re
import random
from pydub import AudioSegment
from io import BytesIO

def app():
    # CSS 스타일 추가
    st.markdown(
        """
        <style>
        p{font-size: 14px;text-align: left;}
        h1{font-size: 36px;}
        div.stButton > button, div.stDownloadButton > button {
            height: 54px;
            font-size: 24px;
        }
        .big-font {font-size: 22.5px; font-weight: bold;} /* 슬라이더와 셀렉트박스 라벨 크기 변경 */
        label {display: block; margin-bottom: 5px;} /* 라벨 스타일 조정 */
        .stSelectbox {margin-bottom: 20px;} /* 셀렉트박스 하단 여백 추가 */
        </style>
        """,
        unsafe_allow_html=True
    )

    def is_input_exist(text):
        pattern = re.compile(r'[a-zA-Z가-힣]')
        return not bool(pattern.search(text))

    def which_eng_kor(input_s):
        count = Counter(input_s)
        k_count = sum(count[c] for c in count if ord('가') <= ord(c) <= ord('힣'))
        e_count = sum(count[c] for c in count if 'a' <= c.lower() <= 'z')
        return "ko" if k_count > e_count else "en"

    def extract_question(text):
        match = re.match(r'(\d{1,2}\s*\.?\s*번?)\s*(.*)', text)
        if match:
            number = match.group(1).strip()
            question = match.group(2).strip()
            return number, question
        else:
            return None, text.lstrip()

    def merge_lines(lines):
        merged = []
        current_sentence = ""
        for line in lines:
            line = line.strip()
            if line.endswith('.') or line.endswith('?') or line.endswith('!'):
                current_sentence += " " + line
                merged.append(current_sentence.strip())
                current_sentence = ""
            else:
                current_sentence += " " + line
        if (current_sentence):
            merged.append(current_sentence.strip())
        return merged

    def get_voice(option, idx, gender):
        if option in ["random", "sequential"]:
            if gender == "female":
                voices = ['alloy', 'fable', 'nova', 'shimmer']
            else:
                voices = ['echo', 'onyx']
            if option == "random":
                selected_voice = random.choice(voices)
                print(f"Randomly selected {gender} voice: {selected_voice}")
                return selected_voice
            else:
                selected_voice = voices[idx % len(voices)]
                print(f"Sequentially selected {gender} voice: {selected_voice}")
                return selected_voice
        else:
            print(f"Selected {gender} voice: {option}")
            return option

    api_key = st.secrets["OPENAI_API_KEY"]

    if not api_key:
        st.error("API key not found. Please set the OPENAI_API_KEY environment variable.")
    else:
        client = OpenAI(api_key=api_key)

        st.title("듣기평가 음원 만들기")
        st.markdown('제작 : 교사 박범진, <br>참고 소스코드 : 박현수 선생님', unsafe_allow_html=True)

        col_speed, col_subheader = st.columns([5, 7])
        with col_speed:
            st.markdown('<p class="big-font">음성 속도(배)</p>', unsafe_allow_html=True)
            speed_rate = st.slider("", 0.55, 1.85, 1.0, 0.05)
        
        voice_selection = st.columns(3)
        with voice_selection[0]:
            st.markdown('<p class="big-font">한국어 음성</p>', unsafe_allow_html=True)
            ko_option = st.selectbox("", ['alloy', 'echo', 'fable', 'nova', 'onyx', 'shimmer'], index=2)
        with voice_selection[1]:
            st.markdown('<p class="big-font">여성 음성</p>', unsafe_allow_html=True)
            female_voice = st.selectbox("", ['alloy', 'fable', 'nova', 'shimmer', "sequential", "random"])
        with voice_selection[2]:
            st.markdown('<p class="big-font">남성 음성</p>', unsafe_allow_html=True)
            male_voice = st.selectbox("", ['echo', 'onyx', "sequential", "random"])

        gap_selection = st.columns(2)
        with gap_selection[0]:
            st.markdown('<p class="big-font">대사 간격(ms)</p>', unsafe_allow_html=True)
            interline = st.slider("", 30, 1000, 200)
        with gap_selection[1]:
            st.markdown('<p class="big-font">문제 간격(s)</p>', unsafe_allow_html=True)
            internum = st.slider("", 1, 15, 5)

        st.markdown("## 유의사항")
        st.markdown("""
        - **음성 생성**: 선택한 음성으로 텍스트를 변환합니다.
        - **음성 옵션**: 'random'은 무작위 음성 선택, 'sequential'은 순차적 음성 변경을 의미합니다.
        - **입력 데이터**: 입력된 텍스트는 음성 변환을 위해 사용되며, 다른 용도로는 사용되지 않습니다.
        """)
        
        st.text_area("대본 입력란", height=300, help="듣기평가 대본을 입력하세요.")

        if st.button("🔊 음원 생성하기"):
            st.balloons()
            st.success("음원이 생성되었습니다.")

app()
