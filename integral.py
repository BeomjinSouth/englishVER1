import streamlit as st
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def app():
    st.title("적분 계산기")
    
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
        if current_sentence:
            merged.append(current_sentence.strip())
        return merged

    def get_voice(option, idx, gender):
        voices = {'female': ['alloy', 'fable', 'nova', 'shimmer'], 'male': ['echo', 'onyx']}
        if option == "random":
            return np.random.choice(voices[gender])
        return voices[gender][idx % len(voices[gender])]

    def plot_func_and_points(func, x_array, y_array):
        x = sp.symbols('x')
        p = sp.plot(func, (x, -2, float(max(x_array)) + 2), show=False)
        p.xlabel = 'x'
        p.ylabel = 'f(x)'

        fig, ax = plt.subplots()
        p[0].line_color = 'red'
        p._backend.fig = fig
        p._backend.ax[0] = ax
        p.show()

        ax.scatter(x_array, y_array, color='blue')
        return fig

    def area(func, x_inf, x_sup, delta_x):
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

        fig, ax = plt.subplots()
        x_plot = np.linspace(x_inf, x_sup, 1000)
        y_plot = f(x_plot)
        ax.plot(x_plot, y_plot, 'r', label='f(x)')

        ax.bar(x_vals[:-1], y_vals[:-1], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='좌측 리만 합')
        ax.bar(x_vals[:-1], y_vals[1:], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='우측 리만 합', color='green')

        ax.legend()
        ax.set_xlabel('x')
        ax.set_ylabel('f(x)')

        return fig, left_riemann_sum, right_riemann_sum

    # Streamlit UI 생성
    st.header("함수와 적분 입력")
    func_input = st.text_input("함수를 입력하세요 (x의 함수):", "x**2")
    x_inf = st.number_input("하한값 (x_inf)을 입력하세요:", value=0.0)
    x_sup = st.number_input("상한값 (x_sup)을 입력하세요:", value=1.0)
    delta_x = st.number_input("리만 합의 델타 x를 입력하세요:", value=0.1, min_value=0.01)

    x = sp.symbols('x')
    func = sp.sympify(func_input)

    if st.button("함수와 점들 그리기"):
        y_vals = [func.subs(x, val) for val in np.arange(x_inf, x_sup, delta_x)]
        fig = plot_func_and_points(func, np.arange(x_inf, x_sup, delta_x), y_vals)
        st.pyplot(fig)

    if st.button("면적 계산하기"):
        area_result = area(func, x_inf, x_sup, delta_x)
        st.write(f"{x_inf}에서 {x_sup}까지 곡선 아래의 면적은: {area_result} 입니다.")

    if st.button("리만 합 그리기"):
        fig, left_riemann_sum, right_riemann_sum = plot_riemann_sums(func, x_inf, x_sup, delta_x)
        st.pyplot(fig)
        st.write(f"좌측 리만 합: {left_riemann_sum}")
        st.write(f"우측 리만 합: {right_riemann_sum}")
