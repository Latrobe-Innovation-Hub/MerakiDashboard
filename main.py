from dash_extensions.enrich import DashProxy, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dash import dcc
from dash_extensions import WebSocket

app = DashProxy(external_stylesheets=[dbc.themes.CYBORG], title="Meraki Test", update_title=None)

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
    dbc.Form(
        [
            dbc.Label("Frame"),
            html.Br(),
            dbc.Spinner(
                dbc.ButtonGroup(
                    [
                        dbc.Button(
                            "Prev", id="prev", n_clicks=0, color="primary", outline=True
                        ),
                        dbc.Button("Next", id="next", n_clicks=0, color="primary"),
                    ],
                    id="button-group",
                    style={"width": "100%"},
                ),
            ),
        ]
    ),
]

app.layout = dbc.Container(
    [
        WebSocket(url='ws://192.168.3.238:4444/ws', id="ws"),
        dbc.Row([dbc.Col(html.H3("Meraki Camera Test"), md=8)]),
        html.Br(),
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
                        dcc.Graph(id="people-counter-graph"),
                        body=True
                    ),
                    md=6
                ),
            ]
        ),
    ],
    fluid=True,
)

@app.callback(
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
   Output("ws", "send"), 
   Input("cameras", "value")
)
def send_camera_id(value):
   print(f"Sending camera ID: {value} to server")
   return value
   
app.clientside_callback(
    """
    function(message) {
        if (message) {
            const blob = new Blob([message.data], { type: 'image/jpeg' });
            const url = URL.createObjectURL(blob);
            document.getElementById('frame-image').src = url;
        }
    }
    """,
    output=Output('frame-image', 'src'),
    inputs=[Input('ws', 'message')]
)


if __name__ == '__main__':
   app.run_server(debug=True, host='0.0.0.0', port=8050)


