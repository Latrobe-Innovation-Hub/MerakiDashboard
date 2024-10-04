import asyncio

class TaskManager():
    def __init__(self):
        self.tasks_list = {}

    async def create_task(self, callback, websocket, request, **kwargs):
        # If there wasn't a task with name (callback.__name__) running, create a new one.
        if callback.__name__ not in self.tasks_list: 
            self.tasks_list[callback.__name__] = asyncio.create_task(callback(websocket, request, **kwargs))
        else: # Else cancel the old task and start a new one.
            self.tasks_list[callback.__name__].cancel()
            try:
                await self.tasks_list[callback.__name__]
            except asyncio.CancelledError:
                print(f"Client {websocket.remote_address} {callback.__name__}_task was cancelled.")
            self.tasks_list[callback.__name__] = asyncio.create_task(callback(websocket, request, **kwargs))
            
    async def cancel_all(self):
        for task in self.tasks_list.values():
            task.cancel()
        await asyncio.gather(*self.tasks_list.values(), return_exceptions=True)
