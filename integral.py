import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

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

    ax.bar(x_vals[:-1], y_vals[:-1], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='Left Riemann Sum')
    ax.bar(x_vals[:-1], y_vals[1:], width=delta_x, align='edge', alpha=0.3, edgecolor='black', label='Right Riemann Sum', color='green')

    ax.legend()
    ax.set_xlabel('x')
    ax.set_ylabel('f(x)')

    return fig, left_riemann_sum, right_riemann_sum
