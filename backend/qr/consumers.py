import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab session_id from the URL (e.g., /ws/transfer/abc123hex/)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"transfer_{self.room_id}"
        
        # Join the specific room for this session
        current_connection_count=cache.get(f"qr_session_count_{self.room_id}") or 0

        if current_connection_count>2:
            self.state="reject"
            await self.close(code=4003)
            return 

        # 2. Atomic increment (Ensure key exists first)
        cache.add(f"qr_session_count_{self.room_id}", 0, timeout=30*60)
        new_connection_count = cache.incr(f"qr_session_count_{self.room_id}")
        
        self.state = "accept"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Ensure session validity keys are active
        cache.set(f"qr_session_pc_{self.room_id}", True, timeout=30)
        cache.set(f"qr_session_mobile_{self.room_id}", True, timeout=30*60)

    async def disconnect(self, close_code):
        if getattr(self, "state", "") == "reject":
            return
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
      
        cache.delete(f"qr_session_pc_{self.room_id}")
        cache.delete(f"qr_session_mobile_{self.room_id}")
        cache.delete(f"qr_session_count_{self.room_id}")
        

    # This method is triggered when the mobile view sends a message
    async def send_file_notification(self, event):
        # Send data to the PC browser
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "file_url": event["file_url"],
            "file_name": event.get("file_name", "Unknown"),
            "message": "File received successfully!"
        }))