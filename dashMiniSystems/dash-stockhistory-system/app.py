import pandas as pd
import dash
from pyecharts import options as opts
import akshare as ak
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from pyecharts.charts import Kline
import feffery_antd_components as fac


# 应用实例化
app = Dash(
    __name__,
    title='量化小应用',
    update_title='加载中...',
    assets_url_path='assets/setting.css'
)

app.layout = fac.AntdSpace([
    dcc.Store(storage_type='local', id='stock-code-store', data=pd.read_excel('data\stock_code.xlsx', dtype={'A股代码': 'str'}).to_dict('records')),
    fac.AntdFlex([
        fac.AntdIcon(icon='antd-right', style={'color': '#0069d9'}),
        fac.AntdText('股票历史日线数据查询', className='header')
    ]),
    fac.AntdFlex([
        fac.AntdFlex([
            '股票代码：',
            dcc.Dropdown(
                id='stock-dropdown',
                multi=False,
                searchable=True,
                value='000001',
                placeholder='股票代码',
                style={'width': '100px'}
            ),
        ], align='center', gap='small'),
        fac.AntdFlex([
            '日期：',
            fac.AntdDateRangePicker(
                placeholder=['选择开始日期', '选择结束日期'],
                id='stock-dropdown datepicker',
                size='middle',
                prefix=fac.AntdIcon(icon='antd-calendar')
            ),
        ], gap='small'),
        fac.AntdButton(
            '搜索',
            type='primary',
            id='stock-dropdown btn',
            loadingChildren="查询中",
        ),
    ], align='center', gap='large'),
    fac.AntdCard(
        title='收益概述',
        headStyle={'background': 'rgba(0, 0, 0, 0.3)', 'text-align': 'left'},
        id='card-content',
        className='card'
    ),
], className='container')


@app.callback(
    Output('stock-dropdown', 'options'),
    Input('stock-code-store', 'data')
)
def code_info(data):
    data = pd.DataFrame(data)
    data['A股代码'] = data['A股代码'].astype('str')
    options = [
        {'label': x, 'value': 'sz' + y}
        for x, y in zip(data['A股代码'], data['A股代码'])
    ]
    return options


@app.callback(
    Output('card-content', 'children'),
     Input('stock-dropdown btn', 'nClicks'),
    [State('stock-code-store', 'data'),
     State('stock-dropdown', 'value'),
     State('stock-dropdown datepicker', 'value')],
    running=[(Output('stock-dropdown btn', "loading"), True, False)],
)
def update(nClicks, data, value, date):
    stock_info = pd.DataFrame(data)

    stock_info = stock_info[stock_info['A股代码'] == value[2:]].to_dict('records')
    title = stock_info[0]['A股简称'] + '(SZ:' + stock_info[0]['A股代码'] + ')'

    result = ak.stock_zh_a_daily(symbol=value, start_date=date[0], end_date=date[1])
    result.rename(columns={'open': '开盘价', 'close': '收盘价', 'low': '最低', 'high': '最高'}, inplace=True)
    fig = (
        Kline(init_opts=opts.InitOpts(width='1200px', height='300px'))
        .add_xaxis(list(result['date']))
        .add_yaxis(series_name='k线', y_axis=result[['开盘价', '收盘价', '最低', '最高']].values.tolist(),
                   itemstyle_opts=opts.ItemStyleOpts(color='rgb(192, 51, 47)', color0='green'))
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f'{date[0]}-{date[1]}日K线'),
            yaxis_opts=opts.AxisOpts(name='单位净值（元）', min_=result[['开盘价', '收盘价', '最低', '最高']].min().min(), max_=result[['开盘价', '收盘价', '最低', '最高']].max().max()),
            tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross', formatter='{b}: {c}', border_color='#ccc', background_color='rgba(245, 245, 245, 0.8)'),
            datazoom_opts=opts.DataZoomOpts(is_show=True, range_start=result['date'].min(), range_end=result['date'].max()),
        )
        .set_series_opts(
            markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_='max', name='最高价', value=result['最高'].max()), opts.MarkPointItem(type_='min', name='最低价', value=result['最低'].min())], symbol='pin'),
            splitline_opts=opts.SplitAreaOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(type_='dashed', color='lightgrey'),
        )
    )
    fig.render('kline.html')

    card_layout = [
        fac.AntdRow(title, className='card-content title', wrap=True),
        fac.AntdRow([
            fac.AntdCol([
                fac.AntdText('最高：', className='card-content index'),
                fac.AntdText(result['最高'].max(), className='card-content value', style={'color': 'red'})
            ]),
            fac.AntdCol([
                fac.AntdText('最低：', className='card-content index'),
                fac.AntdText(result['最低'].max(), className='card-content value', style={'color': 'green'})
            ]),
            fac.AntdCol([
                fac.AntdText(f'成交量：{str(result['volume'].sum())}手', className='card-content index'),]),
            fac.AntdCol([
                fac.AntdText(f'成交额：{str(result['amount'].sum())}元', className='card-content index'),]),
        ], gutter=20),
        html.Iframe(
            srcDoc=open('kline.html', 'r').read(),
            style={
               'height': 300,
               'width': '100%',
               'align': 'center'
            }
        )
    ]
    return card_layout


if __name__ == '__main__':
    app.run(debug=False)
