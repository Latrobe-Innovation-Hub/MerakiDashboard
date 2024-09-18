from dash_extensions.enrich import DashProxy, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from dash import dcc
from dash_extensions import WebSocket

import json

dash.register_page(__name__, path="/")

dih_map = html.Div([
            html.Img(src='assets/dih_crop.jpg', alt='image', id='image', style={
                'width': '100%',
                'height': 'auto',  # Maintain aspect ratio
                'display': 'block'
            }),

            html.Div(id='Q2PV-W8RK-DDVX', style={
                'position': 'absolute',
                'top': '11%', 'left': '46.5%', 'width': '10%', 'height': '20%',
                'backgroundColor': 'rgba(255, 0, 0, 0.2)',
                'cursor': 'pointer',
                'border-radius': '50%'
            }),
            html.Div(id='Q2PV-DZXG-F3GV', style={
                'position': 'absolute',
                'top': '43%', 'left': '74%', 'width': '13%', 'height': '25%',
                'backgroundColor': 'rgba(0, 255, 0, 0.2)',
                'cursor': 'pointer',
                'border-radius': '50%'
            }),
            html.Div(id='Q2PV-EFHS-BMY5', style={
                'position': 'absolute',
                'top': '76%', 'left': '84%', 'width': '10%', 'height': '20%',
                'backgroundColor': 'rgba(0, 0, 255, 0.2)',
                'cursor': 'pointer',
                'border-radius': '50%'
            }),
    ], style={'position': 'relative', 'width': '100%'}
)

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(dih_map, body=True), md=7
                ),
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="people-counter-graph"),
                        body=True
                    ),
                    md=5
                ),
            ]
        ),
    ],
    fluid=True,
)

@callback(
    Output("people-counter-graph", "figure"),
    Input("ws", "message")  # This assumes you will get the data via WebSocket
)
def update_graph(message):
    time_periods = ["1h", "3h", "5h", "1d", "3d", "7d"]
    people_counts = [5, 12, 20, 35, 50, 75]

    figure = {
        'data': [
            {'x': time_periods, 'y': people_counts, 'type': 'bar', 'name': 'People Count'},
        ],
        'layout': {
            'title': 'People Count Over Time',
            'xaxis': {'title': 'Time Period'},
            'yaxis': {'title': 'Number of People'},
        }
    }
    
    return figure

@callback(
    Output("ws", "send", allow_duplicate=True),
    [Input('Q2PV-W8RK-DDVX', 'n_clicks'),
     Input('Q2PV-DZXG-F3GV', 'n_clicks'),
     Input('Q2PV-EFHS-BMY5', 'n_clicks')]
)
def request_people_count(area1, area2, area3):
    if not any([area1, area2, area3]):
        return dash.no_update

    ctx = dash.callback_context
    json_dict = {
        "people_count": {
            "camera_id": ctx.triggered[0]['prop_id'].split('.')[0],
            "date_range": "7d"
        }
    }
    print("Requesting data from the server")
    print(json_dict)
    return json.dumps(json_dict)



