import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def app():
    st.title("적분 계산기")

    # Streamlit UI 생성
    st.header("함수와 적분 입력")
    func_input = st.text_input("함수를 입력하세요 (x의 함수):", "x**2")
    x_inf = st.number_input("하한값 (x_inf)을 입력하세요:", value=0.0)
    x_sup = st.number_input("상한값 (x_sup)을 입력하세요:", value=10.0)
    delta_x = st.number_input("리만 합의 델타 x를 입력하세요:", value=1.0, min_value=0.01)

    def plot_func_and_points(func, x_array, y_array, x_inf, x_sup):
        x = sp.symbols('x')
        f = sp.lambdify(x, func, 'numpy')

        fig, ax = plt.subplots(figsize=(6, 6))  # 600x600 크기로 설정 (인치 단위)
        x_vals = np.linspace(x_inf, x_sup, 1000)
        y_vals = f(x_vals)

        ax.plot(x_vals, y_vals, label=str(func))
        ax.scatter(x_array, y_array, color='red')
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        ax.legend()
        
        # 그래프 x축과 y축 범위 및 비율 조정
        ax.set_xlim(x_inf, x_sup)
        ax.set_ylim(min(y_vals), max(y_vals))
        ax.set_aspect('equal', adjustable='box')

        return fig

    def area(func, x_inf, x_sup):
        x = sp.symbols('x')
        F = sp.integrate(func, x)
        area_result = F.subs(x, x_sup) - F.subs(x, x_inf)
        return area_result

    def plot_riemann_sums(func, x_inf, x_sup, delta_x):
        x = sp.symbols('x')
        f = sp.lambdify(x, func, 'numpy')

        x_vals = np.arange(x_inf, x_sup, delta_x)
        y_vals = f(x_vals)

        left_riemann_sum = np.sum(y_vals[:-1] * delta_x)
        right_riemann_sum = np.sum(y_vals[1:] * delta_x)

        fig, ax = plt.subplots(figsize=(6, 6))  # 600x600 크기로 설정 (인치 단위)
        x_plot = np.linspace(x_inf, x_sup, 1000)
        y_plot = f(x_plot)
        ax.plot(x_plot, y_plot, 'r', label='f(x)')

        ax.bar(x_vals[:-1], y_vals[:-1], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='좌측 리만 합')
        ax.bar(x_vals[:-1], y_vals[1:], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='우측 리만 합', color='green')

        ax.legend()
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')
        
        # 그래프 x축과 y축 범위 및 비율 조정
        ax.set_xlim(x_inf, x_sup)
        ax.set_ylim(min(y_plot), max(y_plot))
        ax.set_aspect('equal', adjustable='box')

        return fig, left_riemann_sum, right_riemann_sum

    # 입력 값 검증
    if '=' in func_input:
        st.error("함수를 입력할 때 'y=' 부분을 제거하고 입력하세요.")
    else:
        x = sp.symbols('x')
        func = sp.sympify(func_input)

        if st.button("함수와 점들 그리기"):
            y_vals = [func.subs(x, val) for val in np.arange(x_inf, x_sup, delta_x)]
            fig = plot_func_and_points(func, np.arange(x_inf, x_sup, delta_x), y_vals, x_inf, x_sup)
            st.pyplot(fig)

        if st.button("면적 계산하기"):
            area_result = area(func, x_inf, x_sup)
            st.write(f"{x_inf}에서 {x_sup}까지 곡선 아래의 면적은: {area_result} 입니다.")

        if st.button("리만 합 그리기"):
            fig, left_riemann_sum, right_riemann_sum = plot_riemann_sums(func, x_inf, x_sup, delta_x)
            st.pyplot(fig)
            st.write(f"좌측 리만 합: {left_riemann_sum}")
            st.write(f"우측 리만 합: {right_riemann_sum}")

