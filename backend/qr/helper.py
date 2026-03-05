import uuid
import qrcode
import base64
from io import BytesIO
def generate_session_id():
    return uuid.uuid4().hex


def get_qr(session_id):
    url=f"http://192.168.1.100:8000/qr/mobile_upload/{session_id}/" # Ideally replace with your PC's actual local IP address

    qr=qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img=qr.make_image(fill_color="black",back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")


    return base64.b64encode(buffer.getvalue()).decode('utf-8')