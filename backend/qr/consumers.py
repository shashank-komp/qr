import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab session_id from the URL (e.g., /ws/transfer/abc123hex/)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"transfer_{self.room_id}"
        
       
        # Safety: Ensure the key exists before incrementing to avoid ValueError crash
        await cache.aadd(f"qr_session_count_{self.room_id}", 0, timeout=30*60)
        connection_count = await cache.aincr(f"qr_session_count_{self.room_id}")
        print(f"[WebSocket CONNECT] Room: {self.room_id} | Atomic Count: {connection_count}")

      
        if connection_count == 2:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_joined_msg",
                    "status": "mobile_connected"
                }
            )

        if connection_count > 2:
          
            self.state = "reject"
            await cache.adecr(f"qr_session_count_{self.room_id}")
            await self.accept()
         
            await self.send(text_data=json.dumps({
                "error": "Room Full",
                "code": 4003
            }))
            await self.close(code=4003)
            return

        self.state = "accept"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        await cache.aset(f"qr_session_active_{self.room_id}", True, timeout=35*60)
        
      
      

    async def disconnect(self, close_code):
        if getattr(self, "state", "") == "reject":
            return
        
        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
     
        await cache.adelete(f"qr_session_active_{self.room_id}")
        await cache.adelete(f"qr_session_count_{self.room_id}")
      
        

    # This method is triggered when the mobile view sends a message
    async def send_file_notification(self, event):
       
        # Send data to the PC browser
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "file_url": event["file_url"],
            "file_name": event.get("file_name", "Unknown"),
            "message": "File received successfully!"
        }))
        print(f"[WebSocket SENT] Room: {self.room_id} | Message transmitted successfully.")

    # This handles the 'user_joined_msg' event sent via group_send
    async def user_joined_msg(self, event):
        await self.send(text_data=json.dumps({
            "type": "CONNECTION_STATUS",
            "status": event["status"],
            "message": "Phone has joined the session!"
        }))