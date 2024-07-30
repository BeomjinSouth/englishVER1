import streamlit as st
from pathlib import Path
from openai import OpenAI

# OpenAI API 클라이언트 초기화
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Streamlit 애플리케이션 제목
st.title('대본 음원 생성기')

# 사용자 입력 받기
script = st.text_area('대본을 입력하세요')

# 재생 속도 및 쉬는 시간 입력 받기
rate = st.slider('재생 속도 (%)', 50, 150, 100)
sentence_pause = st.slider('문장에서 다음 문장으로 넘어갈 때 쉬는 시간 (ms)', 0, 2000, 500)
paragraph_pause = st.slider('문단에서 다음 문단으로 넘어갈 때 쉬는 시간 (ms)', 0, 5000, 1000)

def add_pauses_to_script(script, sentence_pause, paragraph_pause):
    sentences = script.split('.')
    paused_script = ''
    for i, sentence in enumerate(sentences):
        if sentence.strip():
            paused_script += sentence.strip()
            if i < len(sentences) - 1:
                paused_script += f" <break time='{sentence_pause}ms'/>"
    return paused_script

if st.button('생성하기'):
    # 쉬는 시간을 추가한 대본 생성
    paused_script = add_pauses_to_script(script, sentence_pause, paragraph_pause)

    # TTS를 사용하여 대본을 음성으로 변환
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=paused_script
    )
    
    # 음성 파일 저장
    speech_file_path = Path("speech.mp3")
    response.stream_to_file(speech_file_path)
    
    # 음성 파일 재생
    st.audio(str(speech_file_path), format='audio/mp3')
    st.success('음원 생성이 완료되었습니다.')
