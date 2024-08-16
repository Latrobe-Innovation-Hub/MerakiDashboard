from dash_extensions.enrich import DashProxy, html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from dash_extensions import WebSocket

app = DashProxy(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = [
   html.Div(
      id="container",
      children=[
         WebSocket(url='ws://localhost:4444/ws', id="ws"),
         html.Div(
            id="sidebar",
            children=[
               html.H2("Meraki Camera Test"),
               dcc.Dropdown(
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
         html.Div(
            id="content",
            children=[
               dcc.Tabs(
                  id='tabs',
                  value='tab-1',
                  children=[
                     dcc.Tab(label='Camera View', children=[
                        html.H1("WebSocket Frame Display"),
                        html.Img(id="frame-image"),
                     ]),
                     dcc.Tab(label='Graph', children=[
                        html.H2('graph')
                     ]),
                  ]
               ),
               html.Div(id='tabcontent')
            ]
         ),
      ]
   ),
]

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
   app.run_server(debug=True, host='localhost', port=8050)


