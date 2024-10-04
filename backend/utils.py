async def query_people_count(camera_id, date_range, influx_helper):
    query = f'from(bucket:"meraki")\
    |> range(start: -{date_range})\
    |> filter(fn: (r) => r["_measurement"] == "people_count")\
    |> filter(fn:(r) => r.camera_id == "{camera_id}")\
    |> aggregateWindow(every: 1d, fn: mean)'

    return await influx_helper.query(query)