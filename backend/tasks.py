import asyncio
import datetime
import json

import utils

async def influx_task(influx_helper, mqtt_data, map_data_dict):
    while True:
        now = datetime.datetime.now()
        if 8 <= now.hour < 18:  # Between 8 AM and 6 PM
            minutes_to_next = 15 - (now.minute % 15)
            seconds_to_next = minutes_to_next * 60 - now.second

            await influx_helper.write(mqtt_data, map_data_dict)
            await asyncio.sleep(seconds_to_next)
        else:
            # If outside working hours, sleep until 8 AM the next day
            next_run = (now + datetime.timedelta(days=1)).replace(hour=8, minute=0, second=0, microsecond=0)
            time_to_sleep = (next_run - now).total_seconds()
            print(f"Outside working hours. Sleeping until next run at 8 AM: {next_run}")
            await asyncio.sleep(time_to_sleep)

async def send_frame(websocket, request, **kwargs):
    cameras_dict = kwargs.pop('cameras')
    mqtt_data = kwargs.pop('mqtt_data')

    camera = cameras_dict[request["camera_name"]]

    cap = camera["capture"]
    while True:
        bounding_box = mqtt_data[camera["id"]] if camera["id"] in mqtt_data else None
        await websocket.send(cap.get_frame(bounding_box, request["hide_feed"]))
        await asyncio.sleep(1/24)

async def send_people_count(websocket, request, **kwargs):
    cameras_dict = kwargs.pop('cameras')
    influx_helper = kwargs.pop("influx_helper")

    camera = cameras_dict[request["camera_name"]]

    while True:
        json_dict = {
            "people_count": {
                "data": await utils.query_people_count(camera["id"], request["date_range"], influx_helper),
            }
        }
        await websocket.send(json.dumps(json_dict))
        await asyncio.sleep(900) # Send data every 15 minutes

async def send_map_data(websocket, request, **kwargs):
    map_data_dict = kwargs.pop("map_data_dict")
    while True:
        json_dict = {
            "map_data": map_data_dict
        }
        await websocket.send(json.dumps(json_dict))
        await asyncio.sleep(1)