import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab session_id from the URL (e.g., /ws/transfer/abc123hex/)
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"transfer_{self.session_id}"
        
        # Join the specific room for this session
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
       
        cache.set(f"qr_session_pc_{self.session_id}", True,timeout=30)
        cache.set(f"qr_session_mobile_{self.session_id}", True, timeout=30*60)

    async def disconnect(self, close_code):
        # Leave the room and invalidate session if PC or any one in room disconnects
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        cache.delete(f"qr_session_pc_{self.session_id}")
        cache.delete(f"qr_session_mobile_{self.session_id}")
        

    # This method is triggered when the mobile view sends a message
    async def send_file_notification(self, event):
        # Send data to the PC browser
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "file_url": event["file_url"],
            "file_name": event.get("file_name", "Unknown"),
            "message": "File received successfully!"
        }))