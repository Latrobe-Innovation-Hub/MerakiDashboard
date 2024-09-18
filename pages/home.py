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

    html.Div([
        html.P("Workspace", style={'color': 'red', 'text-align': 'center'}),
        html.P("NaN", id="count-Q2PV-W8RK-DDVX", style={'color': 'red', 'text-align': 'center'})
    ], id='Q2PV-W8RK-DDVX', style={
        'position': 'absolute',
        'top': '11%', 'left': '46.5%', 'width': '10%', 'height': '20%',
        'backgroundColor': 'rgba(0, 255, 0, 0.2)',
        'cursor': 'pointer',
        'border-radius': '50%',
        'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'
    }),

    html.Div([
        html.P("Kitchen", style={'color': 'red', 'text-align': 'center'}),
        html.P("NaN", id="count-Q2PV-DZXG-F3GV", style={'color': 'red', 'text-align': 'center'})
    ], id='Q2PV-DZXG-F3GV', style={
        'position': 'absolute',
        'top': '43%', 'left': '74%', 'width': '13%', 'height': '25%',
        'backgroundColor': 'rgba(0, 255, 0, 0.2)',
        'cursor': 'pointer',
        'border-radius': '50%',
        'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'
    }),

    html.Div([
        html.P("Lounge", style={'color': 'red', 'text-align': 'center'}),
        html.P("NaN", id="count-Q2PV-EFHS-BMY5", style={'color': 'red', 'text-align': 'center'})
    ], id='Q2PV-EFHS-BMY5', style={
        'position': 'absolute',
        'top': '76%', 'left': '84%', 'width': '10%', 'height': '20%',
        'backgroundColor': 'rgba(0, 0, 255, 0.2)',
        'cursor': 'pointer',
        'border-radius': '50%',
        'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'
    }),
], style={'position': 'relative', 'width': '100%'})

layout = dbc.Container(
    [
        dcc.Location(id="url"),
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
   Output("ws", "send", allow_duplicate=True), 
   Input("url", "pathname"), prevent_initial_call=False
)
def request_map_data(value):
    json_dict = {
        "map_data": True
    }
    print(f"Requesting map data from server")
    return json.dumps(json_dict)

dash.clientside_callback(
    """
    function(message) {
    console.log(message);
        if (message) {
            let data = JSON.parse(message.data);
            if(data.map_data){
                for(var key in data.map_data)
                {
                    if (data.map_data.hasOwnProperty(key)) {
                        var value = data.map_data[key];
                        document.getElementById(`count-${key}`).innerText = value;
                    }
                }
            }
            
        }
    }
    """,
    Input('ws', 'message')  # Trigger callback when WebSocket message is received
)

@callback(
    Output("people-counter-graph", "figure"),
    Input("ws", "message")  # This assumes you will get the data via WebSocket
)
def update_graph(message):
    if not message:
        return dash.no_update
    else:
        data = json.loads(message['data'])
        if "people_count" not in data:
            return dash.no_update
        
        time_periods = ["1h", "3h", "5h", "1d", "3d", "7d"]
        people_counts = [int(d) for d in data["people_count"]["data"]]  

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
