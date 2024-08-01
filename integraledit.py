def plot_riemann_sums(func, x_inf, x_sup, delta_x):
    x = sp.symbols('x')
    f = sp.lambdify(x, func, 'numpy')
    x_vals = np.arange(x_inf, x_sup, delta_x)
    y_vals = f(x_vals)
    
    # 리만 합을 계산합니다. y_vals는 함수의 y 값들의 배열입니다.
    # 왼쪽 리만 합: 각 구간의 시작점에서 함수 값에 delta_x를 곱합니다.
    left_riemann_sum = np.sum(y_vals[:-1] * delta_x)  # 마지막 점 제외
    # 오른쪽 리만 합: 각 구간의 끝점에서 함수 값에 delta_x를 곱합니다.
    right_riemann_sum = np.sum(y_vals[1:] * delta_x)  # 첫 점 제외
    
    # 그래프를 그리는 부분
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
