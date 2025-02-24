import requests
import re
import time
import pandas as pd
import datetime


def get_stock_data():
    headers = {
        'User-Agent': 'Your User_Agent',    # 换成你的浏览器User-Agent
    }
    now = time.time()
    result = list()
    null = 'null'
    page = 1
    while True:
        url = f'https://push2.eastmoney.com/api/qt/clist/get?np=1&fltt=1&invt=2&cb=jQuery37108988984903378079_{now}&fs=m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80&fields=f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf7%2Cf15%2Cf18%2Cf16%2Cf17%2Cf10%2Cf8%2Cf9%2Cf23&fid=f3&pn={page}&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_={now}'
        response = requests.get(url, headers=headers)
        data = response.text
        r = re.compile('.*\((.*)\).*')
        data = r.findall(data)[0]
        data = eval(data)
        if data['data'] != null:
            for value in data['data']['diff']:
                dict = {
                    '名称': value['f14'],
                    '代码': value['f12'],
                    '最新价': value['f2']/100 if value['f2'] != '-' else '-',
                    '涨跌幅': str(value['f3']/100) + '%' if value['f3'] != '-' else '-',
                    '涨跌额': value['f4']/100 if value['f4'] != '-' else '-',
                    '成交量（手）': value['f5'],
                    '成交额（元）': value['f6'],
                    '振幅': str(value['f7']/100) + '%' if value['f7'] != '-' else '-',
                    '换手率': str(value['f8']/100) + '%' if value['f8'] != 0 else 0,
                    '市盈率': str(value['f9']/100) + '%' if value['f9'] != '-' else '-',
                    '量比': value['f10'],
                    '最高': value['f15']/100 if value['f15'] != '-' else '-',
                    '最低': value['f16']/100 if value['f16'] != '-' else '-',
                    '今开': value['f17']/100 if value['f17'] != '-' else '-',
                    '昨收': value['f18']/100 if value['f18'] != '-' else '-',
                    '市净率': value['f23']/100 if value['f23'] != '-' else '-',
                }
                result.append(dict)
            page += 1
        else:
            break
    return result
    

def data_process(result):
    data = pd.DataFrame(result)
    data['更新时间'] = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    return data


def send_notice():  # 发送通知至桌面函数，按需使用
    title = "提醒"    # 设置通知的内容
    message = "这是一个来自Python的桌面通知！"

    # 发送通知
    notification.notify(
        title=title,
        message=message,
        app_name="my app",  # 应用名称，会显示在通知中
        timeout=10,  # 通知持续时间（秒），0表示直到用户手动关闭
        ticker="预警",  # 在某些系统上，这是状态栏的短暂文本提示
    )

    # 等待一段时间，以便能看到通知（可选）
    time.sleep(60)


if __name__ == '__main__':
    result = get_stock_data()
    result = data_process(result)
    result.to_excel('stock_data.xlsx')
    send_notice()