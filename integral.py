import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# 데이터 입력 받기
st.title("Riemann Sum and Integration")
st.write("데이터 포인트를 입력하세요:")

xlist = []
ylist = []

for i in range(1, 7):
    data_x = st.number_input(f"Data {i} x", format="%f")
    data_y = st.number_input(f"Data {i} y", format="%f")
    xlist.append(data_x)
    ylist.append(data_y)

# 3차 다항식 생성
x_array = np.array(xlist)
y_array = np.array(ylist)
coefficients = np.polyfit(x_array, y_array, 3)
x = sp.symbols('x')
func = coefficients[0] * x**3 + coefficients[1] * x**2 + coefficients[2] * x + coefficients[3]

st.write("다항함수:")
st.latex(sp.pretty(func))

# 다항식과 데이터 포인트 시각화
fig, ax = plt.subplots()
p = sp.plot(func, (x, -2, float(max(x_array)) + 2), show=False)
p[0].line_color = 'red'
p._backend.fig = fig
p._backend.ax[0] = ax
p.show()

ax.scatter(x_array, y_array, color='blue')
st.pyplot(fig)

# 적분 구간 및 Δx 입력 받기
st.write("적분 구간과 Δx 값을 입력하세요:")
x_inf = st.number_input("x_inf", format="%f")
x_sup = st.number_input("x_sup", format="%f")
delta_x = st.number_input("Δx", format="%f")

if st.button("Calculate Area and Plot Riemann Sums"):
    # 정적분 계산
    F = sp.integrate(func, x)
    area = F.subs(x, x_sup) - F.subs(x, x_inf)
    st.write("정적분 결과:")
    st.latex(sp.pretty(area))

    # 리만 합 시각화
    f = sp.lambdify(x, func, 'numpy')
    x_vals = np.arange(x_inf, x_sup, delta_x)
    y_vals = f(x_vals)

    left_riemann_sum = np.sum(y_vals[:-1] * delta_x)
    right_riemann_sum = np.sum(y_vals[1:] * delta_x)

    fig, ax = plt.subplots()
    x_plot = np.linspace(x_inf, x_sup, 1000)
    y_plot = f(x_plot)
    ax.plot(x_plot, y_plot, 'r', label='f(x)')

    ax.bar(x_vals[:-1], y_vals[:-1], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='Left Riemann Sum')
    ax.bar(x_vals[:-1], y_vals[1:], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='Right Riemann Sum', color='green')

    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')

    st.pyplot(fig)

    st.write(f"Left Riemann Sum: {left_riemann_sum}")
    st.write(f"Right Riemann Sum: {right_riemann_sum}")
