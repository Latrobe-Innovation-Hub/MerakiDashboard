import json
import re
import tasks

import paho.mqtt.client as mqtt
import asyncio
import websockets

from influx_helper import InfluxHelper
from task_manager import TaskManager

cameras = {
    "Q2PV-W8RK-DDVX":"rtsp://192.168.3.73:9000/live",
    "test":"rtsp://192.168.3.79:9000/live",
    "Q2PV-DZXG-F3GV":"rtsp://192.168.3.77:9000/live",
    "Q2PV-PQVS-ABKL":"rtsp://192.168.3.76:9000/live",
    "Q2FV-BY6K-RKDN":"rtsp://192.168.3.85:9000/live",
    "Q2PV-EFHS-BMY5":"rtsp://192.168.3.78:9000/live"
}

influx_helper = InfluxHelper(
    url="http://localhost:8086",
    token="test-token",
    org="digital-hub",
    bucket="meraki"
)

mqtt_data = {}
map_data_dict = {}

def on_message(client, userdata, message):
    global mqtt_data
    payload = json.loads(message.payload)
    camera_id = re.search(r'/([A-Z0-9\-]+)/custom_analytics', message.topic).group(1)

    if 'outputs' in payload:
        people_count = 0
        for detection in payload['outputs']:
            if(detection["class"] == 0):
                people_count = people_count + 1

        map_data_dict[camera_id] = people_count
        mqtt_data[camera_id] = payload['outputs']
        
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for camera in cameras:
        client.subscribe(f"/merakimv/{camera}/custom_analytics")

async def handler(websocket, path):
    try:
        task_manager = TaskManager()
        print(f"New client connected: {websocket.remote_address}")
        while True:
            requests = json.loads(await websocket.recv())
            print(f"Client {websocket.remote_address} requested: {requests}")

            if "frame" in requests:
                await task_manager.create_task(tasks.send_frame, websocket, requests["frame"], cameras=cameras, mqtt_data=mqtt_data)
            if "people_count" in requests:
                await task_manager.create_task(tasks.send_people_count, websocket, requests["people_count"], influx_helper=influx_helper)
            if "map_data" in requests:
                await task_manager.create_task(tasks.send_map_data, websocket, requests["map_data"], map_data_dict=map_data_dict)

    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed):
        task_manager.cancel_all()
        print(f"Client {websocket.remote_address} disconnected. Waiting for a new connection...")
    except Exception as e:
        print(f"Error on the server: {str(e)}")

async def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('192.168.3.161', 1883, 60)
    client.loop_start()

    influx_task_ = asyncio.create_task(tasks.influx_task(influx_helper, mqtt_data, map_data_dict))

    start_server = await websockets.serve(handler, "0.0.0.0", 4444)
    print("WebSocket server started.")

    await asyncio.gather(influx_task_, start_server.wait_closed())

if __name__ == "__main__":
    asyncio.run(main())