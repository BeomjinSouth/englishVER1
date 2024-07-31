import streamlit as st
from integral import merge_lines, get_voice, plot_func_and_points, area, plot_riemann_sums

st.title("듣기평가 음원 만들기 및 리만 합 계산기")

# 든기평가 음원 만들기 부분
st.header("듣기평가 음원 만들기: En Listen")
st.write("듣기평가 음원 만들기 기능입니다. (이전 코드 사용)")

# 리만 합 및 정적분 계산 부분
st.header("리만 합 및 정적분 계산")
st.write("데이터 포인트를 입력하세요:")

xlist = []
ylist = []

for i in range(1, 7):
    data_x = st.number_input(f"Data {i} x", format="%f")
    data_y = st.number_input(f"Data {i} y", format="%f")
    xlist.append(data_x)
    ylist.append(data_y)

# 3차 다항식 생성 버튼
if st.button("Generate Polynomial"):
    x_array = np.array(xlist)
    y_array = np.array(ylist)
    coefficients = np.polyfit(x_array, y_array, 3)
    x = sp.symbols('x')
    func = coefficients[0] * x**3 + coefficients[1] * x**2 + coefficients[2] * x + coefficients[3]
    
    st.write("다항함수:")
    st.latex(sp.pretty(func))

    # 다항식과 데이터 포인트 시각화
    fig = plot_func_and_points(func, x_array, y_array)
    st.pyplot(fig)

# 적분 구간 및 Δx 입력 받기
st.write("적분 구간과 Δx 값을 입력하세요:")
x_inf = st.number_input("x_inf", format="%f")
x_sup = st.number_input("x_sup", format="%f")
delta_x = st.number_input("Δx", format="%f")

# 적분 계산 버튼
if st.button("Calculate Area and Plot Riemann Sums"):
    area_result = area(func, x_inf, x_sup, delta_x)
    st.write("정적분 결과:")
    st.latex(sp.pretty(area_result))

    # 리만 합 시각화
    fig, left_riemann_sum, right_riemann_sum = plot_riemann_sums(func, x_inf, x_sup, delta_x)
    st.pyplot(fig)

    st.write(f"Left Riemann Sum: {left_riemann_sum}")
    st.write(f"Right Riemann Sum: {right_riemann_sum}")
