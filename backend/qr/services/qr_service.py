import uuid
import qrcode
import base64
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()   


class QrService:

    @staticmethod
    def generate_room_id():
        return uuid.uuid4().hex

    @staticmethod
    def generate_qr_base64(session_id):
        frontend_url = os.environ.get("QR_URL", " ")
        url = f"{frontend_url}/upload-document/{session_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
