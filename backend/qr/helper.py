
def generate_room_id():
    return uuid.uuid4().hex


import os

def get_qr(session_id):
    frontend_url = os.environ.get("QR_URL"," ")
    url = f"{frontend_url}/upload-document/{session_id}"

    qr=qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    img=qr.make_image(fill_color="black",back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# allowed_file_types = ['.jpg', '.jpeg', '.png', '.pdf']
# allowed_mime_types = ['image/jpeg', 'image/png', 'application/pdf']
# allowed_file_size = 25 * 1024 * 1024  # 25MB in bytes