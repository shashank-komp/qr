import os
from qr.services.qr_service import QrService
from qr.services.session_service import SessionService

class GenerateQrInteractor:

    @staticmethod
    def execute():
        room_id=QrService.generate_room_id()
        qr_code=QrService.generate_qr_base64(room_id)
        SessionService.create_session(room_id)
        
      

        return {
            "room_id": room_id,
            "qr_code": qr_code
        }