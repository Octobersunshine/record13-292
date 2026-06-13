import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

DEFAULT_MAX_POINTS = 5000
VALID_SAMPLE_METHODS = ('random', 'equidistant', 'first')


def sample_data(x_np, y_np, max_points, method):
    n = len(x_np)
    if n <= max_points:
        return x_np, y_np, False

    if method == 'random':
        rng = np.random.default_rng()
        indices = rng.choice(n, size=max_points, replace=False)
        indices.sort()
    elif method == 'equidistant':
        indices = np.linspace(0, n - 1, max_points, dtype=int)
    else:
        indices = np.arange(max_points)

    return x_np[indices], y_np[indices], True


def compute_linear_regression(x_np, y_np):
    if len(x_np) < 2:
        return None, None, None, None, None

    valid_mask = np.isfinite(x_np) & np.isfinite(y_np)
    x_valid = x_np[valid_mask]
    y_valid = y_np[valid_mask]

    if len(x_valid) < 2:
        return None, None, None, None, None

    slope, intercept = np.polyfit(x_valid, y_valid, 1)
    y_pred = slope * x_valid + intercept
    ss_res = np.sum((y_valid - y_pred) ** 2)
    ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    return slope, intercept, r_squared, np.min(x_valid), np.max(x_valid)


def build_trend_label(slope, intercept, r_squared):
    sign = '+' if intercept >= 0 else '-'
    abs_intercept = abs(intercept)
    formula = f'y = {slope:.4f}x {sign} {abs_intercept:.4f}'
    return f'{formula} (R²={r_squared:.4f})'


@app.route('/scatter', methods=['POST'])
def generate_scatter():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({'error': '请求体为空，请提供 JSON 数据'}), 400

        if 'x' not in data or 'y' not in data:
            return jsonify({'error': '缺少必要字段 "x" 和 "y"'}), 400

        x = data['x']
        y = data['y']

        if not isinstance(x, list) or not isinstance(y, list):
            return jsonify({'error': '"x" 和 "y" 必须为数组'}), 400

        if len(x) != len(y):
            return jsonify({'error': '"x" 和 "y" 数组长度必须一致'}), 400

        if len(x) == 0:
            return jsonify({'error': '"x" 和 "y" 数组不能为空'}), 400

        try:
            x_np = np.array(x, dtype=float)
            y_np = np.array(y, dtype=float)
        except (ValueError, TypeError):
            return jsonify({'error': '"x" 和 "y" 数组中的元素必须为数字'}), 400

        title = data.get('title', '散点图')
        xlabel = data.get('xlabel', 'X 轴')
        ylabel = data.get('ylabel', 'Y 轴')
        color = data.get('color', '#1f77b4')
        size = data.get('size', 50)
        alpha = data.get('alpha', 0.7)
        dpi = data.get('dpi', 100)
        max_points = data.get('max_points', DEFAULT_MAX_POINTS)
        sample_method = data.get('sample_method', 'random')
        show_trendline = data.get('show_trendline', False)
        trendline_color = data.get('trendline_color', '#d62728')
        trendline_width = data.get('trendline_width', 2)
        trendline_alpha = data.get('trendline_alpha', 0.9)
        show_formula = data.get('show_formula', False)
        regression_use_original = data.get('regression_use_original', True)

        if not isinstance(max_points, int) or max_points < 1:
            return jsonify({'error': '"max_points" 必须为正整数'}), 400

        if sample_method not in VALID_SAMPLE_METHODS:
            return jsonify({'error': f'"sample_method" 必须为 {VALID_SAMPLE_METHODS} 之一'}), 400

        if not isinstance(trendline_width, (int, float)) or trendline_width <= 0:
            return jsonify({'error': '"trendline_width" 必须为正数'}), 400

        if not isinstance(trendline_alpha, (int, float)) or not (0 < trendline_alpha <= 1):
            return jsonify({'error': '"trendline_alpha" 必须在 (0, 1] 范围内'}), 400

        original_count = len(x_np)
        x_plot, y_plot, sampled = sample_data(x_np, y_np, max_points, sample_method)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x_plot, y_plot, c=color, s=size, alpha=alpha, edgecolors='white', linewidth=0.5, zorder=2)

        trend_info = None
        if show_trendline:
            if regression_use_original:
                slope, intercept, r_squared, x_min, x_max = compute_linear_regression(x_np, y_np)
            else:
                slope, intercept, r_squared, x_min, x_max = compute_linear_regression(x_plot, y_plot)

            if slope is not None:
                x_line = np.linspace(x_min, x_max, 200)
                y_line = slope * x_line + intercept
                trend_label = build_trend_label(slope, intercept, r_squared)
                ax.plot(x_line, y_line, color=trendline_color, linewidth=trendline_width,
                        alpha=trendline_alpha, linestyle='-', zorder=3, label=trend_label)

                if show_formula:
                    ax.legend(loc='best', fontsize=10, framealpha=0.8)

                trend_info = {
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r_squared': float(r_squared)
                }

        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        title_display = f'{title}' if not sampled else f'{title}（采样 {len(x_plot)}/{original_count}）'
        ax.set_title(title_display, fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6, zorder=1)
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=dpi)
        buf.seek(0)
        plt.close(fig)

        response = send_file(buf, mimetype='image/png')
        if sampled:
            response.headers['X-Sampled'] = 'true'
            response.headers['X-Original-Count'] = str(original_count)
            response.headers['X-Sampled-Count'] = str(len(x_plot))
        if trend_info is not None:
            response.headers['X-Trend-Slope'] = f"{trend_info['slope']:.8f}"
            response.headers['X-Trend-Intercept'] = f"{trend_info['intercept']:.8f}"
            response.headers['X-Trend-R2'] = f"{trend_info['r_squared']:.8f}"
        return response

    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': '散点图服务运行正常'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
