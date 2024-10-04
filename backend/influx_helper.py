import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

import json

class InfluxHelper():
    def __init__(self, url, token, org, bucket):
        self.org = org
        self.bucket = bucket
        self.client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()

    async def write(self, mqtt_data, map_data_dict):
        for camera_id, raw_data in mqtt_data.copy().items():
            for detection in raw_data:
                if(detection["class"] == 0):
                    p = influxdb_client.Point("detections") \
                        .tag("camera_location", "digital_hub") \
                        .tag("camera_id", camera_id) \
                        .field("bounding_box", json.dumps(detection["location"])) \
                        .field("id", json.dumps(detection["id"])) \
                        .field("score", json.dumps(detection["score"]))
                    self.write_api.write(bucket=self.bucket, org=self.org, record=p, write_precision=WritePrecision.S)

            p = influxdb_client.Point("people_count") \
                .tag("camera_location", "digital_hub") \
                .tag("camera_id", camera_id) \
                .field("people_count", map_data_dict[camera_id])
            self.write_api.write(bucket=self.bucket, org=self.org, record=p, write_precision=WritePrecision.S)

    async def query(self, query):
        result = self.query_api.query(org=self.org, query=query)
        data = []
        for table in result:
            for record in table.records:
                value = record.get_value()
                if value is not None:
                    data.append(round(value))
                else:
                    data.append(0)
        
        return data