import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash()

# 读取数据文件
df = pd.read_csv('googleplaystore.csv')
df = df.dropna(axis=0, how="any")
categories = df['Category'].unique() # 获取所有的类别

# 计算每个类别的安装量
installation_num = []
for n in categories:
    total = 0
    dff = df[df['Category'] == n]['Installs']
    for d in dff:
        d = d[0:-1]
        d = d.replace(',', '')
        d = int(d)
        total += d
    installation_num.append(total)

# 画饼图
CategoryInstallationNumberPieGraph = go.Figure(data=go.Pie(
    labels=categories,
    values=installation_num,
    hoverinfo='label+value+percent',
    textinfo='none',
    customdata=categories
),
layout=go.Layout(
    title='Installation Number of Each Category'
))

# 计算每个类别的评分并创建数据框
dfRateCount = df.Rating.value_counts()
maxCount = max(dfRateCount)
dfRateCount = {'Rating': dfRateCount.index, 'Count': dfRateCount.values}
dfRateCount = pd.DataFrame(dfRateCount)
dfRateCount = dfRateCount.sort_values(by="Rating", ascending=True)

# 画柱状图
CategoryRatingsBarGraph = go.Figure(
    data=go.Bar(
        x=dfRateCount.Rating,
        y=dfRateCount['Count'].astype(int),
        customdata=dfRateCount.Count,
    ),
    layout=go.Layout(
        yaxis={
            'title': 'App Count',
        },
        xaxis={
            'title': 'Rating',
        },
        title='App Count of Each Rating',
    )
)

# 页面布局
app.layout = html.Div(
    [
        # 页面布局的顶部
        html.Div(
            [
                html.Div(
                    [
                        dcc.RadioItems(
                            id='type',
                            options=[{'label': type, 'value': type} for type in ['Linear', 'Log']],
                            value='Log',
                            labelStyle={'display': 'inline-block', 'margin-left': '80%'}
                        )
                    ],
                    style={'width': '45%', 'display': 'inline-block', 'margin-left': '45%'}
                )
            ],
            style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '10px 5px'
            }
        ),
        # 左侧圆形图
        html.Div(
            dcc.Graph(
                id='circleGraph',
                figure=CategoryInstallationNumberPieGraph,
                hoverData={'points': [{'customdata': 'ART_AND_DESIGN'}]}
            ),
            style={'display': 'inline-block', 'width': '49%'}
        ),
        # 右上图和右下图
        html.Div(
            [
                dcc.Graph(id='graph1'),
                dcc.Graph(id='graph2')
            ],
            style={'display': 'inline-block', 'width': '49%'}
        ),
        # 柱状图
        html.Div(
            dcc.Graph(
                id='Graph',
                figure=CategoryRatingsBarGraph
            ),
            style={'width': '100%', 'display': 'inline-block', 'padding': '0 20'}
        )
    ]
)

@app.callback(
    Output('graph1', 'figure'),
    [
        Input('type', 'value'),
        Input('circleGraph', 'hoverData')
    ]
)
def updateGraph1(type, hoverData):
    dff = df[df['Category'] == hoverData['points'][0]['customdata']]
    ydata = dff['Installs']
    yData = []
    for yd in ydata:
        yd = yd[0:-1]
        yd = yd.replace(',', '')
        yd = int(yd)
        yData.append(yd)
    s = dff['Size']
    size = []
    for _s in s:
        if _s == 'Varies with device':
            size.append(0)
            continue
        if 'M' in _s:
            _s = _s.split('M')[0]
            _s = float(_s)
        elif 'k' in _s:
            _s = _s.split('k')[0]
            _s = float(_s) / 1024
        size.append(_s / 2)
    return {
        'data': [go.Scatter(
            x=dff['Rating'].astype(float),
            y=yData,
            mode='markers',
            text=dff['App'] + '<br> Last updated: ' + dff['Last Updated'] + '<br>Size: ' + dff['Size'],
            customdata=dff['App'],
            marker={
                'size': size,
                'opacity': 0.5,
                'color': 'blue',
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': {
            'margin': {'l': 50, 'b': 30, 'r': 10, 't': 10},
            'height': 225,
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': hoverData['points'][0]['customdata']
            }],
            'yaxis': {
                'title': 'Installations',
                'type': 'linear' if type == 'Linear' else 'log'
            },
            'xaxis': {
                'title': 'Rating',
                'showgrid': True
            },
            'hovermode': 'closest'
        }
    }


@app.callback(Output('graph2', 'figure'),
              [Input('circleGraph', 'hoverData'),
               Input('type', 'value')])
def updateGraph2(hoverData, type):
    # 根据选定的 Category 进行筛选
    dff = df[df['Category'] == hoverData['points'][0]['customdata']]
    
    return {
        'data': [go.Scatter(
            x=dff['Rating'].astype(float),
            y=dff['Reviews'].astype(int),
            mode='markers',
            text=dff['App'] + '<br> Last updated: ' + dff['Last Updated'] + '<br>Size: ' + dff['Size'],
            customdata=dff['App'],
            marker={
                'size': 10,
                'opacity': 0.5,
                'color': 'red',
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': {
            'margin': {'l': 50, 'b': 30, 'r': 10, 't': 10},
            'height': 225,
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': hoverData['points'][0]['customdata']
            }],
            'yaxis': {
                'title': 'Reviews',
                'type': 'linear' if type == 'Linear' else 'log'
            },
            'xaxis': {
                'title': 'Rating',
                'showgrid': True
            },
            'hovermode': 'closest'
        }
    }


# 运行
if __name__ == '__main__':
    app.run_server()
