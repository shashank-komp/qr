import uuid
import qrcode
import base64
from io import BytesIO


def generate_session_id():
    return uuid.uuid4().hex


import os

def get_qr(session_id):
    frontend_url = os.environ.get("FRONTEND_URL", "https://qr-eight-self.vercel.app")
    url = f"{frontend_url}/qr/mobile_upload/{session_id}"

    qr=qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img=qr.make_image(fill_color="black",back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")


    return base64.b64encode(buffer.getvalue()).decode('utf-8')