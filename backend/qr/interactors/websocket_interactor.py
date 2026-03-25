from qr.services.session_service import SessionService, MAX_CONNECTIONS

class WebSocketInteractor:

    @staticmethod
    async def handle_connection(room_id):
        try:
            connection_count = await SessionService.increment_connection_count(room_id)
        except ValueError:
            return {
                "status": "reject", 
                "code": 4004, 
                "msg_type": "INVALID_QR_STATUS",
                "message": "Invalid QR"
            }

        if connection_count > MAX_CONNECTIONS:
            await SessionService.decrement_connection_count(room_id)
            return {
                "status": "reject",
                "code": 4003, 
                "msg_type": "ROOM_FULL_STATUS",
                "message": "QR has already been scanned"
            }

        await SessionService.mark_session_active(room_id)

        return {
            "status": "accept",
            "is_mobile": connection_count == MAX_CONNECTIONS
        }

    @staticmethod
    async def handle_session_data(room_id, incoming_data):
        return await SessionService.update_session_data(room_id, incoming_data)

    @staticmethod
    async def handle_cleanup(room_id):
        await SessionService.clear_session(room_id)