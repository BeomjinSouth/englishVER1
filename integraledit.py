import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

# 전역 변수로 그림과 계산 결과를 저장
results = []

def app():
    st.title("적분 계산기")
    st.header("함수와 적분 입력")
    func_input = st.text_input("함수를 입력하세요 (x의 함수):", "x**2")
    x_inf = st.number_input("하한값 (x_inf)을 입력하세요:", value=0.0)
    x_sup = st.number_input("상한값 (x_sup)을 입력하세요:", value=10.0)
    delta_x = st.number_input("리만 합의 델타 x를 입력하세요:", value=1.0, min_value=0.01)

    if '=' in func_input:
        st.error("함수를 입력할 때 'y=' 부분을 제거하고 입력하세요.")
    else:
        x = sp.symbols('x')
        func = sp.sympify(func_input)

        if st.button("리만 합 그리기"):
            fig, left_riemann_sum, right_riemann_sum = plot_riemann_sums(func, x_inf, x_sup, delta_x)
            difference = abs(left_riemann_sum - right_riemann_sum)
            results.append({
                "fig": fig,
                "left_sum": left_riemann_sum,
                "right_sum": right_riemann_sum,
                "difference": difference
            })
            display_results()

        if st.button("그림 모두 지우기"):
            results.clear()
            st.write("모든 그림이 제거되었습니다. 페이지를 새로 고침하세요.")

def plot_riemann_sums(func, x_inf, x_sup, delta_x):
    x = sp.symbols('x')
    f = sp.lambdify(x, func, 'numpy')
    x_vals = np.arange(x_inf, x_sup, delta_x)
    y_vals = f(x_vals)

    left_riemann_sum = np.sum(y_vals[:-1] * delta_x)
    right_riemann_sum = np.sum(y_vals[1:] * delta_x)

    fig, ax = plt.subplots(figsize=(4, 4))
    x_plot = np.linspace(x_inf, x_sup, 1000)
    y_plot = f(x_plot)

    ax.plot(x_plot, y_plot, 'r', label='f(x)')
    ax.bar(x_vals[:-1], y_vals[:-1], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='Left Riemann Sum')
    ax.bar(x_vals[:-1], y_vals[1:], width=delta_x, align='edge', alpha=0.3, edgecolor='black', color='green', label='Right Riemann Sum')
    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')
    ax.set_xlim(x_inf, x_sup)
    ax.set_ylim(min(y_plot), max(y_plot))
    ax.set_aspect('equal', adjustable='box')

    return fig, left_riemann_sum, right_riemann_sum

def display_results():
    for result in results:
        st.pyplot(result["fig"])
        st.write(f"좌측 리만 합: {result['left_sum']:.2f}")
        st.write(f"우측 리만 합: {result['right_sum']:.2f}")
        st.write(f"리만 합 차이: {result['difference']:.2f}")

if __name__ == "__main__":
    app()
