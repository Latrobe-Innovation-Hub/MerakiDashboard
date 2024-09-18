from dash_extensions.enrich import DashProxy, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from dash import dcc
from dash_extensions import WebSocket

import json

dash.register_page(__name__)

controls = [
    dbc.Form(
        [
            dbc.Label("Select Camera"),
            dbc.Select(
                id='cameras',
                value='Q2PV-W8RK-DDVX',
                placeholder="Select or search a camera",
                options=[
                    {'label': 'Workspace', 'value': 'Q2PV-W8RK-DDVX'},
                    {'label': 'Kitchen', 'value': 'Q2PV-DZXG-F3GV'},
                    {'label': 'Entry', 'value': 'Q2PV-PQVS-ABKL'},
                    {'label': 'Entry-non-fisheye', 'value': 'Q2FV-BY6K-RKDN'},
                    {'label': 'Lounge', 'value': 'Q2PV-EFHS-BMY5'}
                ]
            )
        ]
    ),
]

layout = dbc.Container(
    [
        dbc.Card(dbc.Row([dbc.Col(c) for c in controls]), body=True),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        html.Img(id="frame-image", style={"width": "100%", "height": "auto"}),
                        body=True
                    ), 
                    md=6
                ),
                dbc.Col(
                    dbc.Card(
                        dcc.Graph(id="dummy"),
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
   Output("ws", "send"), 
   Input("cameras", "value")
)
def send_camera_id(value):
    json_dict = {
        "frame": {
            "camera_id": value,
        }
    }
    print(f"Sending camera ID: {json.dumps(json_dict)} to server")
    return json.dumps(json_dict)
   
dash.clientside_callback(
    """
    function(message) {
        if (message) {
            let data = JSON.parse(message.data);
            
            if (data.frame) {
                const blob = new Blob([data.frame.data], { type: 'image/jpeg' });
                const url = URL.createObjectURL(blob);
                document.getElementById('frame-image').src = url;
            }
        }
    }
    """,
    inputs=[Input('ws', 'message')]
)


