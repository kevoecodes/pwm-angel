from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
from bson import json_util

from users_managements.mongo_crud import OnlineUpdate, MongoCheck


class User_DevUpdates_Consumer(AsyncJsonWebsocketConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        print(self.scope['path_remaining'])
        self.accountNo = self.scope['path_remaining']
        self.thread_name = f"thread_{self.accountNo}"
        print(self.thread_name)
        await self.channel_layer.group_add(
            self.thread_name,
            self.channel_name
        )
        OnlineUpdate(True, self.deviceNo)
        await self.accept()
        await self.fetch_device_data()
        await self.send_json(json.loads(json_util.dumps(self.device_data)))

    async def websocket_receive(self, event):
        print("Message: ", event['text'])

        await self.channel_layer.group_send(
            "thread_1",
            {
                "type": "send.message",
                "data": event['text']
            }
        )

    async def send_message(self, event):
        print('messages', event)

        await self.send_json(event['data'])

    async def websocket_disconnect(self, event):
        print("disonnected", event)
        OnlineUpdate(False, self.deviceNo)
        await self.channel_layer.group_discard(
            self.thread_name,
            self.channel_name
        )
        await self.disconnect(event['code'])
        raise StopConsumer()

    @database_sync_to_async
    def fetch_device_data(self):
        data = MongoCheck({"accountNo": self.accountNo})
        self.device_data = data.feedback()

