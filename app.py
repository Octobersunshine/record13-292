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

        if not isinstance(max_points, int) or max_points < 1:
            return jsonify({'error': '"max_points" 必须为正整数'}), 400

        if sample_method not in VALID_SAMPLE_METHODS:
            return jsonify({'error': f'"sample_method" 必须为 {VALID_SAMPLE_METHODS} 之一'}), 400

        original_count = len(x_np)
        x_plot, y_plot, sampled = sample_data(x_np, y_np, max_points, sample_method)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(x_plot, y_plot, c=color, s=size, alpha=alpha, edgecolors='white', linewidth=0.5)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        title_display = f'{title}' if not sampled else f'{title}（采样 {len(x_plot)}/{original_count}）'
        ax.set_title(title_display, fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6)
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
        return response

    except Exception as e:
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': '散点图服务运行正常'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
