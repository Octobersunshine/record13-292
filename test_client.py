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
        print('=' * 50)
        print('测试完成！')
    except requests.exceptions.ConnectionError:
        print('连接失败！请先启动服务: python app.py')
