from dash_extensions.enrich import DashProxy, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash
from dash import dcc
from dash_extensions import WebSocket

import json

app = DashProxy(external_stylesheets=[dbc.themes.CYBORG], title="Meraki Test", update_title=None, use_pages=True)

app.layout = dbc.Container(
    [
        WebSocket(url='ws://192.168.3.238:4444/ws', id="ws"),
        dbc.Row([dbc.Col(html.H3("Meraki Camera Test"), md=8)]),
        html.Br(),
        dash.page_container
    ],
    fluid=True,
)

if __name__ == '__main__':
   app.run_server(debug=True, host='0.0.0.0', port=8050)


