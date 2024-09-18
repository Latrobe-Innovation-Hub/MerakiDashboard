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
query_api = client.query_api()

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

                p = influxdb_client.Point("detections") \
                    .tag("camera_location", "digital_hub") \
                    .tag("camera_id", camera_id) \
                    .field("bounding_box", json.dumps(detection["location"])) \
                    .field("id", json.dumps(detection["id"])) \
                    .field("score", json.dumps(detection["score"]))
                write_api.write(bucket=bucket, org=org, record=p, write_precision=WritePrecision.S)

        mqtt_data[camera_id] = payload['outputs']
        map_data_dict[camera_id] = people_count
        p = influxdb_client.Point("people_count") \
            .tag("camera_location", "digital_hub") \
            .tag("camera_id", camera_id) \
            .field("people_count", people_count)
        write_api.write(bucket=bucket, org=org, record=p, write_precision=WritePrecision.S)
        
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for camera in cameras:
        client.subscribe(f"/merakimv/{camera}/custom_analytics")

def query_people_count(camera_id, date_range):
    query = f'from(bucket:"meraki")\
    |> range(start: -{date_range})\
    |> filter(fn: (r) => r["_measurement"] == "people_count")\
    |> filter(fn:(r) => r.camera_id == "{camera_id}")\
    |> aggregateWindow(every: 1d, fn: mean)'

    result = query_api.query(org=org, query=query)
    data = []
    for table in result:
        for record in table.records:
            value = record.get_value()
            if value is not None:
                data.append(round(value))
            else:
                data.append(0)
    
    return data

async def send_frame(websocket, request):
    try:
        cap = MerakiCamera(cameras[request["camera_id"]])
        while True:
            json_dict = {
                "frame": {
                    "data": cap.get_frame(mqtt_data[request["camera_id"]]),
                }
            }
            await websocket.send(json.dumps(json_dict))
            await asyncio.sleep(1/24)
    except asyncio.CancelledError:
        raise

async def send_people_count(websocket, request):
    try:
        while True:
            json_dict = {
                "people_count": {
                    "data": query_people_count(request["camera_id"], request["date_range"]),
                }
            }
            await websocket.send(json.dumps(json_dict))
            await asyncio.sleep(900) # Send data every 15 minutes
    except asyncio.CancelledError:
        raise

async def send_map_data(websocket, request):
    try:
        while True:
            json_dict = {
                "map_data": map_data_dict
            }
            await websocket.send(json.dumps(json_dict))
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        raise   
    except Exception as e:
        print(e)

async def handler(websocket, path):
    global mqtt_data
    global map_data_dict
    client_ip, client_port = websocket.remote_address
    tasks = {}

    try:
        print(f"New client connected: {client_ip}:{client_port}")
        while True:
            requests = json.loads(await websocket.recv())
            print(f"Client {client_ip}:{client_port} requested: {requests}")

            if "frame" in requests:
                # If there wasn't a frame task running, create a new one.
                if "frame" not in tasks: 
                    tasks["frame"] = asyncio.create_task(send_frame(websocket, requests["frame"]))
                else: # Else cancel the old task and start a new one.
                    tasks["frame"].cancel()
                    try:
                        await tasks["frame"]
                    except asyncio.CancelledError:
                        print(f"Client {client_ip}:{client_port} frame-task was cancelled.")
                    tasks["frame"] = asyncio.create_task(send_frame(websocket, requests["frame"]))
            elif "people_count" in requests:
                if "people_count" not in tasks: 
                    tasks["people_count"] = asyncio.create_task(send_people_count(websocket, requests["people_count"]))
                else: # Else cancel the old task and start a new one.
                    tasks["people_count"].cancel()
                    try:
                        await tasks["people_count"]
                    except asyncio.CancelledError:
                        print(f"Client {client_ip}:{client_port} people_count-task was cancelled.")
                    tasks["people_count"] = asyncio.create_task(send_people_count(websocket, requests["people_count"]))
            elif "map_data" in requests:
                tasks["map_data"] = asyncio.create_task(send_map_data(websocket, requests["map_data"]))

    except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosed):
        for task in tasks.values():
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
