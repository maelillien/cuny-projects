# DATA608 Final Project - Cryptocurrency Screener
#

import cbpro
import time
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime
from re import search
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Authenticate public client to coinbase pro
public_client = cbpro.PublicClient()

# Returns a list of the cryptocurrency/USD pairs
def getProductIds(output='dict'):
    products = [p['id'] for p in public_client.get_products() if search(r'-USD$', p['id'])]
    if output == 'dict':
        return [{'label': p, 'value': p} for p in sorted(products)]
    else:
        return products

# Returns the name of the cryptocurrency as a string
def getProductName(product_id):
    id_name = {c['id']: c['name'] for c in public_client.get_currencies()}
    return id_name[product_id.replace('-USD', '')]

# Returns a list of the intervals
def getIntervals():
    intervals = [('1m', 60), ('5m', 300), ('15m', 900), ('1h', 3600), ('6h', 21600), ('D', 86400)]
    # intervals = {'1m': 60, '5m': 300, '15m': 900, '1h': 3600, '6h': 21600, 'D': 86400}
    return [{'label': key, 'value': value} for key, value in intervals]

# Returns a dataframe with historical prices (OHLCV) for a given symbol and interval
def getHistoricalData(product_id='BTC-USD', interval=60):
    json_list = public_client.get_product_historic_rates(product_id, granularity=interval)
    data = pd.DataFrame(json_list, columns=['time', 'low', 'high', 'open', 'close', 'volume'])
    data['time'] = data['time'].apply(lambda x: datetime.utcfromtimestamp(x).isoformat())
    data['time'] = pd.to_datetime(data['time'])
    return data

# Returns the screener dash_table.DataTable component
def get_screener():
    screener = pd.DataFrame(columns=['productId','productName','last','7day%','30day%'])

    for product_id in getProductIds(list):
        try:
            hist_data = getHistoricalData(product_id=product_id, interval=86400)
            # Calculate columns and append to dataframe
            hist_data_last = hist_data.iloc[0,:].close
            hist_data_w = hist_data.iloc[7,:].close
            hist_data_m = hist_data.iloc[30,:].close
            screener = screener.append({'productId': product_id,
                                 'productName': getProductName(product_id),
                                 'last': hist_data_last,
                                 '7day%': round((hist_data_last-hist_data_w)/hist_data_w*100,1),
                                 '30day%': round((hist_data_last-hist_data_m)/hist_data_m*100,1)},
                                ignore_index=True)
            time.sleep(0.01)
        except IndexError:
            hist_data_m = 'NA'

    screener_table = dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i}
                 for i in screener.columns],
        data=screener.to_dict('records'),
        style_as_list_view=True,
        style_header={'backgroundColor': 'white',
                       'fontWeight': 'bold'},
        sort_action="native",
        css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
        style_cell={
            'textAlign':'left',
            'width': '{}%'.format(len(screener.columns)),
            'textOverflow': 'ellipsis',
            'overflow': 'hidden'
        },
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{7day%} > 0',
                    'column_id': '7day%'
                },
                'color': 'green'
            },
            {
                'if': {
                    'filter_query': '{7day%} < 0',
                    'column_id': '7day%'
                },
                'color': 'red'
            },
            {
                'if': {
                    'filter_query': '{30day%} > 0',
                    'column_id': '30day%'
                },
                'color': 'green'
            },
            {
                'if': {
                    'filter_query': '{30day%} < 0',
                    'column_id': '30day%'
                },
                'color': 'red'
            }
        ]
    )

    return screener_table

## Layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='Cryptocurrency Screener'),
    html.Div(className='row',  # Define the row element
             children=[
                 html.Div(className='two columns div-user-controls',
                          children=[
                              html.Label('Select symbol:'),
                              dcc.Dropdown(
                                  options=getProductIds(output='dict'),
                                  value='BTC-USD',
                                  id='dropdown-product'
                              ),
                              html.Label('Select an interval:'),
                              dcc.Dropdown(
                                  options=getIntervals(),
                                  value=60,
                                  id='dropdown-interval'
                              ),
                              html.Label('Select graph type:'),
                              dcc.Dropdown(
                                  options=[
                                      {'label': 'line', 'value': 'line'},
                                      {'label': 'candle', 'value': 'candle'}
                                  ],
                                  value='candle',
                                  id='dropdown-graph'
                              ),
                              html.Label('Add indicator:'),
                              dcc.Dropdown(
                                  options=[
                                      {'label': 'SMA', 'value': 'SMA'}
                                  ],
                                  multi=True,
                                  value=[],
                                  id='dropdown-indicator'
                              ),
                              html.Div(id='indicator-output-container',
                                       children=[
                                                "Enter SMA window:",
                                                dcc.Input(
                                                    id="input-sma", type="number", placeholder="",
                                                    min=1, max=100, step=1,
                                                )
                              ]),
                              html.Label('Select symbols to compare:'),
                              dcc.Dropdown(
                                  options=getProductIds(output='dict'),
                                  multi=True,
                                  value=['BTC-USD'],
                                  id='dropdown-compare'
                              ),
                              html.Div(id='vol-slider-output-container'),
                              dcc.Slider(
                                min=3,
                                max=50,
                                step=1,
                                value=7,
                                id='volatility-slider'
                              )
                          ]
                          ),  # End of left element

                 html.Div(className='ten columns div-user-controls',
                          children=[
                              html.Div(className='seven columns div-left-display',
                                    children=[
                                        dcc.Graph(
                                            id='stacked-charts'
                                        )
                                    ]
                                    ),  # End of left chart element
                              html.Div(className='five columns div-right-display',
                                    children=[
                                        get_screener()
                                    ]
                                    )  # End of right chart element

                          ]
                          )  # End of right element
             ])

])

## Callbacks

@app.callback(
    Output('stacked-charts', 'figure'),
    [Input('dropdown-product','value'),
     Input('dropdown-compare', 'value'),
     Input('dropdown-graph', 'value'),
     Input('input-sma', 'value'),
     Input('dropdown-interval', 'value'),
     Input('volatility-slider','value')])
def stackedPlots(product_id, product_list, graph, sma_window, interval=60, vol_window=5):

    fig = make_subplots(rows=4, cols=1)

    # Price Data
    data = getHistoricalData(product_id, interval)
    price = data[['time', 'close']]
    price = price.set_index('time')

    if graph == "line":
        fig.append_trace(go.Scatter(
            x=price.index,
            y=price.close,
        ), row=1, col=1)
    else:
        fig.append_trace(go.Candlestick(x=data['time'],
                                        open=data['open'], high=data['high'],
                                        low=data['low'], close=data['close']),
                         row=1, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False)

    # Indicators
    if sma_window:
        mavg = price.copy()
        mavg = mavg[::-1]
        #mavg['ma'] = talib.MA(mavg['close'], timeperiod=sma_window)
        mavg['ma'] = mavg['close'].rolling(sma_window).mean()
        fig.append_trace(go.Scatter(
            x=mavg.index,
            y=mavg.ma,
            line=dict(color='black')
        ), row=1, col=1)

    # Volume
    fig.append_trace(go.Bar(
        x=data.time,
        y=data.volume,
    ), row=2, col=1)

    # Cummulative Returns
    for p in product_list:
        data_ = getHistoricalData(p, interval=interval)
        price_ = data_[['time', 'close']]
        price_ = price_.set_index('time')
        col = price_[::-1]
        col.columns = [p]
        returns = col.pct_change()
        cumreturns = (1.0 + returns).cumprod()-1.0
        # df = pd.concat([df, cumreturns], axis=1)
        fig.add_trace(go.Scatter(x=cumreturns.index, y=cumreturns[p], mode='lines', name=p,
                                 hovertemplate = "return: %{y:.2%}<br>"),row=3, col=1)

    # Volatility (not annualized)
    returns = price.pct_change()
    logreturns = np.log(price/price.shift(1))
    ann_vol = {60: 1440, 300: 288, 900: 96, 3600: 24, 21600: 4, 86400: 1}
    vol = logreturns[::-1].rolling(vol_window).std() # * np.sqrt(252*ann_vol[interval])

    fig.append_trace(go.Scatter(
        x=vol.index,
        y=vol.close
    ), row=4, col=1)

    fig.update_layout({'showlegend': False,
                       'yaxis': {'title': 'Price', 'tickformat':'$'},
                       'yaxis2': {'title':'Volume'},
                       'yaxis3': {'title': 'Cummulative Returns', 'tickformat':'.0%'},
                       'yaxis4': {'title': 'Rolling Volatility'},
                       'plot_bgcolor': 'rgb(255,255,255)'}
                      )
    fig.update_layout(height=800, width=700)

    return fig

@app.callback(
    Output('vol-slider-output-container', 'children'),
    [Input('volatility-slider', 'value')])
def update_volatility(value):
    return 'Volatility window size: {}'.format(value)


@app.callback(
    Output('indicator-output-container', component_property='style'),
    [Input('dropdown-indicator', 'value')])
def show_indicators(dropdown_value):

    if dropdown_value:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

if __name__ == '__main__':
    app.run_server(debug=True)
