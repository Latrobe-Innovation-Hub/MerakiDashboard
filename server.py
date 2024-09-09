import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision
import json

import paho.mqtt.client as mqtt
import re

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
    camera_id = re.search(r'/([A-Z0-9\-]+)/custom_analytics', message.topic).group(1)

    if 'outputs' in payload:
        mqtt_data = payload['outputs']
        for detection in payload['outputs']:
            p = influxdb_client.Point("detections") \
                .tag("camera_location", "digital_hub") \
                .tag("camera_id", camera_id) \
                .tag("class", detection["class"]) \
                .field("location", json.dumps(detection["location"])) \
                .time(payload['timestamp'], write_precision=WritePrecision.MS)
            write_api.write(bucket=bucket, org=org, record=p)
        
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for camera in cameras:
        client.subscribe(f"/merakimv/{camera}/custom_analytics")

async def send_frame(websocket, camera_id):
    try:
        cap = MerakiCamera(cameras[camera_id])
        while True:
            await websocket.send(cap.get_frame(mqtt_data))
            await asyncio.sleep(1/24)
    except asyncio.CancelledError:
        raise

async def handler(websocket, path):
    global mqtt_data
    client_ip, client_port = websocket.remote_address
    tasks = {}

    try:
        print(f"New client connected: {client_ip}:{client_port}")
        while True:
            requests = json.loads(await websocket.recv())
            print(f"Client {client_ip}:{client_port} requested: {requests}")

            if requests["frame"]:
                # If there wasn't a frame task running, create a new one.
                if "frame" not in tasks: 
                    tasks["frame"] = asyncio.create_task(send_frame(websocket, requests["camera_id"]))
                else: # Else cancel the old task and start a new one.
                    tasks["frame"].cancel()
                    try:
                        await tasks["frame"]
                    except asyncio.CancelledError:
                        print(f"Client {client_ip}:{client_port} frame-task was cancelled.")
                    tasks["frame"] = asyncio.create_task(send_frame(websocket, requests["camera_id"]))
            elif requests["people_count"]:
                print("People count requested")
                # TODO: Implement people count logic here.

    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed):
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks.values(), return_exceptions=True)
        print(f"Client {client_ip}:{client_port} disconnected. Waiting for a new connection...")
    except Exception as e:
        print(f"Error on the server: {str(e)}")

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()

    start_server = websockets.serve(handler, "0.0.0.0", 4444)
    print("WebSocket server started.")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
