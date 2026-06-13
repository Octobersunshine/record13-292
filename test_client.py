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
        print('=' * 50)
        print('测试完成！')
    except requests.exceptions.ConnectionError:
        print('连接失败！请先启动服务: python app.py')
