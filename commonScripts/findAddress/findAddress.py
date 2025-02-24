import requests


def run(address):
    header = {
        'User-Agent': 'Your User-Agent',
    }
    url = f'https://restapi.amap.com/v3/geocode/geo?address={address}&key={Your Key}'
    response = requests.get(url, headers=header)
    return response.json()


if __name__ == '__main__':
    dict = run('北京市北京大学')
    print(dict)
