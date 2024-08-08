import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 사용자로부터 나무막대 길이 입력 받기
st.title('삼각형 만들기 웹앱')
st.write('나무막대의 길이를 입력하세요 (cm)')

a = st.number_input('막대 1 길이', min_value=1, max_value=100)
b = st.number_input('막대 2 길이', min_value=1, max_value=100)
c = st.number_input('막대 3 길이', min_value=1, max_value=100)

angle_a = st.slider('막대 1의 각도', 0, 360, 0)
angle_b = st.slider('막대 2의 각도', 0, 360, 0)
angle_c = st.slider('막대 3의 각도', 0, 360, 0)

fig, ax = plt.subplots()
x = np.array([0, a, b * np.cos(np.radians(angle_b))])
y = np.array([0, 0, b * np.sin(np.radians(angle_b))])
x = np.append(x, c * np.cos(np.radians(angle_c)))
y = np.append(y, c * np.sin(np.radians(angle_c)))

ax.plot([x[0], x[1]], [y[0], y[1]], marker='o')
ax.plot([x[1], x[2]], [y[1], y[2]], marker='o')
ax.plot([x[2], x[0]], [y[2], y[0]], marker='o')

ax.set_xlim(-max(a, b, c), max(a, b, c))
ax.set_ylim(-max(a, b, c), max(a, b, c))
ax.set_aspect('equal')
st.pyplot(fig)

st.write('각도를 조정하여 삼각형을 만들어보세요.')
