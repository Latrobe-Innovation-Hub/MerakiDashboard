import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json

import cv2
import paho.mqtt.client as mqtt

from dash import Dash, html, dcc, Input, Output

#################### InfluxDB Configuration ####################
bucket = "meraki"
org = "digital-hub"
token = "test-token"
url="http://localhost:8086"

#################### MQTT Configuration ####################
mqtt_broker = 'localhost'
mqtt_port = 1883
mqtt_topic = "/merakimv/Q2PV-W8RK-DDVX/custom_analytics"
rtsp_url = "rtsp://192.168.3.76:9000/live"
save_path = "."
image_filename = "capture.jpg"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

def on_message(client, userdata, message):
   #print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

   payload = json.loads(message.payload)
   if 'outputs' in payload:
      p = influxdb_client.Point("detections").tag("location", "digital_hub").field("output", json.dumps(payload['outputs']))
      write_api.write(bucket=bucket, org=org, record=p, write_precision='ms')

def on_connect(client, userdata, flags, rc):
   print(f"Connected with result code {rc}")
   client.subscribe(mqtt_topic)

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

app = Dash()

app.layout = [
   html.Div(
      id="container",
      children=[
         html.Div(
            id="sidebar",
            children=[
               html.H2("Meraki Camera Test"),
               dcc.Dropdown(
                  id='cars',
                  value='Workspace',
                  options=[
                     {'label': 'Workspace', 'value': 'Q2PV-W8RK-DDVX'},
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
                        html.H2('camera')
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

if __name__ == '__main__':
   app.run(debug=True)
   #client.connect("localhost", 1883, 60)
   #client.loop_forever()
