import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab session_id from the URL (e.g., /ws/transfer/abc123hex/)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"transfer_{self.room_id}"
        
       
        # The room is already initialized in views.py:generate_qr
        connection_count = await cache.aincr(f"qr_session_count_{self.room_id}")

        print(f"[WebSocket CONNECT] Room: {self.room_id} | Atomic Count: {connection_count}")

        if connection_count > 2:
            print(f"[WebSocket REJECTED] Room: {self.room_id} is full (Count: {connection_count})")
            self.state = "reject"
            await cache.adecr(f"qr_session_count_{self.room_id}")
            await self.accept()
            # Send a clear message so the user sees WHY it closed in Postman
            await self.send(text_data=json.dumps({
                "error": "Room Full",
                "code": 4003
            }))
            await self.close(code=4003)
            return

        self.state = "accept"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Now that the group is joined, mark the session as active so the phone can upload
        await cache.aset(f"qr_session_active_{self.room_id}", True, timeout=30*60)
        
        print(f"[WebSocket ACCEPTED] Room: {self.room_id} | Session Secure.")
        
      

    async def disconnect(self, close_code):
        if getattr(self, "state", "") == "reject":
            return
        
        print(f"[WebSocket DISCONNECT] Room: {self.room_id} | Code: {close_code} | Wiping session...")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
     
        await cache.adelete(f"qr_session_active_{self.room_id}")
        await cache.adelete(f"qr_session_count_{self.room_id}")
        print(f"[WebSocket VIPED] Room: {self.room_id} | Session cleared.")
        

    # This method is triggered when the mobile view sends a message
    async def send_file_notification(self, event):
        print(f"[WebSocket NOTIFY] Room: {self.room_id} | Sending file: {event.get('file_name')} to PC...")
        # Send data to the PC browser
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "file_url": event["file_url"],
            "file_name": event.get("file_name", "Unknown"),
            "message": "File received successfully!"
        }))
        print(f"[WebSocket SENT] Room: {self.room_id} | Message transmitted successfully.")