import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json

import paho.mqtt.client as mqtt

import asyncio
import websockets
from meraki_camera import MerakiCamera

cameras = {
    "Q2PV-W8RK-DDVX":"rtsp://192.168.3.73:9000/live",
    "Q2PV-DZXG-F3GV":"rtsp://192.168.3.77:9000/live",
    "Q2PV-PQVS-ABKL":"rtsp://192.168.3.76:9000/live",
    "Q2FV-BY6K-RKDN":"rtsp://192.168.3.85:9000/live",
    "Q2PV-EFHS-BMY5":"rtsp://192.168.3.78:9000/live"
}

################### MQTT Configuration ####################
mqtt_broker = '192.168.3.161'
mqtt_port = 1883
camera_id = "Q2PV-W8RK-DDVX"
mqtt_topic = f"/merakimv/{camera_id}/custom_analytics"

################### InfluxDB Configuration ####################
bucket = "meraki"
org = "digital-hub"
token = "test-token"
url="http://localhost:8086"

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)
write_api = client.write_api(write_options=SYNCHRONOUS)

mqtt_data = None

def on_message(client, userdata, message):
    global mqtt_data
    payload = json.loads(message.payload)

    if 'outputs' in payload:
        p = influxdb_client.Point("detections").tag("location", "digital_hub").tag("camera_id", camera_id).field("output", json.dumps(payload['outputs']))
        write_api.write(bucket=bucket, org=org, record=p, write_precision='ms')
        mqtt_data = payload['outputs']
        
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic)

async def send_frame(websocket, path):
    global mqtt_data

    try:
        print("Client connected.")
        new_camera_id = None
        while True:

            if new_camera_id is None:
                camera_id = await websocket.recv()
                print(f"Camera ID: {camera_id}")
            
            cap = MerakiCamera(cameras[camera_id])
            while True:
                await asyncio.sleep(1/10)

                await websocket.send(cap.get_frame(mqtt_data))

                if websocket.messages:
                    new_camera_id = await websocket.recv()
                    if new_camera_id != camera_id:
                        print(f"New Camera ID received: {new_camera_id}")
                        camera_id = new_camera_id
                        del cap
                        break

    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected. Waiting for a new connection...")

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()

    start_server = websockets.serve(send_frame, "localhost", 4444)
    print("WebSocket server started.")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
