import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from apps.accounts.models import DriverLocation

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"driver_{self.user.uid}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    
    async def receive(self, text_data):
        data = json.loads(text_data)
        latitude = data["latitude"]
        longitude = data["longitude"]

        # save location
        await self.update_location(latitude, longitude)

    @sync_to_async
    def update_location(self, latitude, longitude):
        DriverLocation.objects.update_or_create(
            driver=self.user,
            defaults={
                'latitude': latitude,
                'longitude': longitude,
            }
        )
