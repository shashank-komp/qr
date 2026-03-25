import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .interactors.websocket_interactor import WebSocketInteractor

class FileTransferConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grab session_id from the URL (e.g., /ws/transfer/abc123hex/)
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"transfer_{self.room_id}"
        
        result = await WebSocketInteractor.handle_connection(self.room_id)

        if result["status"] == "reject":
            self.state = "reject"
            await self.accept()
            await self.send(text_data=json.dumps({
                "type": result["msg_type"],
                "status": "error",
                "message": result["message"]
            }))
            await self.close(code=result["code"])
            return
        
        self.state = "accept"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        if result["is_mobile"]:
            await self._broadcast("user_joined_msg", status="mobile_connected")
        
      
      

    async def receive(self, text_data):
      
        try:
            data = json.loads(text_data)
            
            if data.get("type") == "SESSION_DATA":

                session_data = await WebSocketInteractor.handle_session_data(self.room_id, data.get("data", {}))

                await self._broadcast("session_data_msg", data=session_data)

            elif data.get("type") == "FILE_UPLOADED":
                await self._broadcast("send_file_notification", 
                    status="uploaded", 
                    file_url=data.get("file_url", ""), 
                    file_name=data.get("file_name", "Unknown"), 
                    method=data.get("method", "mobile")
                )
                # Cleanup
                await WebSocketInteractor.handle_cleanup(self.room_id)

        except json.JSONDecodeError:
            pass

    async def disconnect(self, close_code):
        if getattr(self, "state", "") != "reject":
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            await WebSocketInteractor.handle_cleanup(self.room_id)

   

    async def _broadcast(self, msg_type, **kwargs):
        await self.channel_layer.group_send(self.room_group_name, {"type": msg_type, **kwargs})

    async def session_data_msg(self, event):

        await self.send(text_data=json.dumps({
            "type": "SESSION_DATA",
            "data": event["data"],
        }))

  
      
        


    async def send_file_notification(self, event):
       
   
        await self.send(text_data=json.dumps({
            "status": event["status"],
            "file_url": event["file_url"],
            "file_name": event.get("file_name", "Unknown"),
            "message": "File received successfully!",
            "method":event["method"]
        }))


    
    async def user_joined_msg(self, event):
        await self.send(text_data=json.dumps({
            "type": "CONNECTION_STATUS",
            "status": event["status"],
            "message": "Phone has joined the session!"
        }))

#if file is sent then event to kill all sessions        