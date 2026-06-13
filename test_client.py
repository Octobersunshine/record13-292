import requests
import json
import random


def test_health():
    url = 'http://localhost:5000/health'
    resp = requests.get(url)
    print(f'健康检查: {resp.status_code} {resp.json()}')
    return resp.status_code == 200


def test_scatter_basic():
    url = 'http://localhost:5000/scatter'
    data = {
        'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'y': [2.5, 3.7, 4.2, 5.1, 6.0, 6.8, 7.5, 8.2, 9.0, 10.1],
        'title': '基础散点图示例',
        'xlabel': '时间 (小时)',
        'ylabel': '数值'
    }
    resp = requests.post(url, json=data)
    print(f'基础散点图: {resp.status_code}, Content-Type: {resp.headers.get("Content-Type")}')
    if resp.status_code == 200:
        with open('scatter_basic.png', 'wb') as f:
            f.write(resp.content)
        print('已保存到 scatter_basic.png')
        return True
    else:
        print(f'错误: {resp.json()}')
        return False


def test_scatter_random():
    url = 'http://localhost:5000/scatter'
    n = 100
    data = {
        'x': [random.uniform(0, 10) for _ in range(n)],
        'y': [random.uniform(0, 20) for _ in range(n)],
        'title': '100 个随机点散点图',
        'xlabel': '随机 X',
        'ylabel': '随机 Y',
        'color': '#ff6347',
        'size': 40,
        'alpha': 0.6,
        'dpi': 150
    }
    resp = requests.post(url, json=data)
    print(f'随机散点图: {resp.status_code}, Content-Type: {resp.headers.get("Content-Type")}')
    if resp.status_code == 200:
        with open('scatter_random.png', 'wb') as f:
            f.write(resp.content)
        print('已保存到 scatter_random.png')
        return True
    else:
        print(f'错误: {resp.json()}')
        return False


def test_scatter_validation():
    url = 'http://localhost:5000/scatter'
    data = {'x': [1, 2, 3], 'y': [1, 2]}
    resp = requests.post(url, json=data)
    print(f'参数校验测试 (长度不一致): {resp.status_code} {resp.json()}')
    return resp.status_code == 400


def test_scatter_large_random():
    url = 'http://localhost:5000/scatter'
    n = 100000
    data = {
        'x': [random.uniform(0, 100) for _ in range(n)],
        'y': [random.uniform(0, 100) for _ in range(n)],
        'title': '10万点随机采样',
        'xlabel': 'X',
        'ylabel': 'Y',
        'max_points': 5000,
        'sample_method': 'random'
    }
    import time
    start = time.time()
    resp = requests.post(url, json=data)
    elapsed = time.time() - start
    print(f'大数据量 (random采样): {resp.status_code}, 耗时={elapsed:.2f}s')
    if resp.status_code == 200:
        print(f'  X-Sampled: {resp.headers.get("X-Sampled")}')
        print(f'  X-Original-Count: {resp.headers.get("X-Original-Count")}')
        print(f'  X-Sampled-Count: {resp.headers.get("X-Sampled-Count")}')
        with open('scatter_large_random.png', 'wb') as f:
            f.write(resp.content)
        print('  已保存到 scatter_large_random.png')
        return True
    else:
        print(f'  错误: {resp.json()}')
        return False


def test_scatter_large_equidistant():
    url = 'http://localhost:5000/scatter'
    n = 50000
    data = {
        'x': [i * 0.001 for i in range(n)],
        'y': [i * 0.001 + random.uniform(-0.5, 0.5) for i in range(n)],
        'title': '5万点等距采样',
        'xlabel': 'X',
        'ylabel': 'Y',
        'max_points': 3000,
        'sample_method': 'equidistant'
    }
    import time
    start = time.time()
    resp = requests.post(url, json=data)
    elapsed = time.time() - start
    print(f'大数据量 (equidistant采样): {resp.status_code}, 耗时={elapsed:.2f}s')
    if resp.status_code == 200:
        print(f'  X-Sampled: {resp.headers.get("X-Sampled")}')
        print(f'  X-Original-Count: {resp.headers.get("X-Original-Count")}')
        print(f'  X-Sampled-Count: {resp.headers.get("X-Sampled-Count")}')
        with open('scatter_large_equidistant.png', 'wb') as f:
            f.write(resp.content)
        print('  已保存到 scatter_large_equidistant.png')
        return True
    else:
        print(f'  错误: {resp.json()}')
        return False


def test_scatter_small_no_sampling():
    url = 'http://localhost:5000/scatter'
    data = {
        'x': list(range(50)),
        'y': [random.uniform(0, 10) for _ in range(50)],
        'title': '小数据不采样',
        'max_points': 5000,
        'sample_method': 'random'
    }
    resp = requests.post(url, json=data)
    print(f'小数据量 (无采样): {resp.status_code}, X-Sampled={resp.headers.get("X-Sampled", "未采样")}')
    return resp.status_code == 200


def test_trendline_with_formula():
    url = 'http://localhost:5000/scatter'
    n = 30
    data = {
        'x': [i for i in range(n)],
        'y': [2.1 * i + 3.5 + random.uniform(-4, 4) for i in range(n)],
        'title': '带趋势线和公式的散点图',
        'xlabel': '广告投入',
        'ylabel': '销售额',
        'show_trendline': True,
        'show_formula': True,
        'trendline_color': '#2ca02c',
        'trendline_width': 2.5
    }
    resp = requests.post(url, json=data)
    print(f'趋势线+公式: {resp.status_code}')
    if resp.status_code == 200:
        print(f'  X-Trend-Slope: {resp.headers.get("X-Trend-Slope")}')
        print(f'  X-Trend-Intercept: {resp.headers.get("X-Trend-Intercept")}')
        print(f'  X-Trend-R2: {resp.headers.get("X-Trend-R2")}')
        with open('scatter_trendline_formula.png', 'wb') as f:
            f.write(resp.content)
        print('  已保存到 scatter_trendline_formula.png')
        return True
    else:
        print(f'  错误: {resp.json()}')
        return False


def test_trendline_large_data_original_regression():
    url = 'http://localhost:5000/scatter'
    n = 80000
    data = {
        'x': [random.uniform(0, 50) for _ in range(n)],
        'y': [],
        'title': '8万点 用原始数据回归',
        'xlabel': 'X',
        'ylabel': 'Y',
        'max_points': 3000,
        'sample_method': 'random',
        'show_trendline': True,
        'show_formula': True,
        'regression_use_original': True,
        'trendline_color': '#9467bd',
        'color': '#1f77b4'
    }
    for xi in data['x']:
        data['y'].append(-0.6 * xi + 50.0 + random.uniform(-8, 8))

    import time
    start = time.time()
    resp = requests.post(url, json=data)
    elapsed = time.time() - start
    print(f'大数据+趋势线(原始回归): {resp.status_code}, 耗时={elapsed:.2f}s')
    if resp.status_code == 200:
        print(f'  X-Sampled: {resp.headers.get("X-Sampled")}')
        print(f'  X-Trend-Slope: {resp.headers.get("X-Trend-Slope")}')
        print(f'  X-Trend-R2: {resp.headers.get("X-Trend-R2")}')
        with open('scatter_large_trend_original.png', 'wb') as f:
            f.write(resp.content)
        print('  已保存到 scatter_large_trend_original.png')
        return True
    else:
        print(f'  错误: {resp.json()}')
        return False


def test_trendline_sampled_regression():
    url = 'http://localhost:5000/scatter'
    n = 100
    data = {
        'x': [i * 0.5 for i in range(n)],
        'y': [0.8 * (i * 0.5) ** 1.2 + random.uniform(-5, 5) for i in range(n)],
        'title': '无趋势线（开关关闭）',
        'xlabel': 'X',
        'ylabel': 'Y',
        'show_trendline': False
    }
    resp = requests.post(url, json=data)
    print(f'无趋势线(开关关闭): {resp.status_code}, X-Trend-Slope={resp.headers.get("X-Trend-Slope", "无")}')
    if resp.status_code == 200:
        with open('scatter_no_trendline.png', 'wb') as f:
            f.write(resp.content)
        print('  已保存到 scatter_no_trendline.png')
        return True
    return False


if __name__ == '__main__':
    print('=' * 50)
    print('开始测试散点图服务...')
    print('=' * 50)

    try:
        test_health()
        print()
        test_scatter_basic()
        print()
        test_scatter_random()
        print()
        test_scatter_validation()
        print()
        test_scatter_small_no_sampling()
        print()
        test_scatter_large_random()
        print()
        test_scatter_large_equidistant()
        print()
        test_trendline_with_formula()
        print()
        test_trendline_large_data_original_regression()
        print()
        test_trendline_sampled_regression()
        print()
        print('=' * 50)
        print('测试完成！')
    except requests.exceptions.ConnectionError:
        print('连接失败！请先启动服务: python app.py')
