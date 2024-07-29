import streamlit as st
from pathlib import Path
from openai import OpenAI

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key='YOUR_OPENAI_API_KEY')

# Streamlit 애플리케이션 제목
st.title('대본 음원 생성기')

# 사용자 입력 받기
script = st.text_area('대본을 입력하세요')

# 음성 선택
voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
voice = st.selectbox("음성을 선택하세요", voice_options)

if st.button('생성하기'):
    # TTS를 사용하여 대본을 음성으로 변환
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=script
    )
    
    # 음성 파일 저장
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response.stream_to_file(speech_file_path)
    
    # 음성 파일 재생
    st.audio(str(speech_file_path), format='audio/mp3')
    st.success('음원 생성이 완료되었습니다.')
