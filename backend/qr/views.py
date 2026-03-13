from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .helper import generate_session_id,get_qr
from rest_framework.decorators import api_view
from .models import Files
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
from django.core.cache import cache
from PIL import Image
import io

@api_view(["GET"])
def gen_qr(request):
    session_id = generate_session_id()
    qr = get_qr(session_id)

    # from token get user id
    user_id = request.get('user_id')
    time=30
        
 

    return JsonResponse({
        "session_id": session_id,
        "qr_code": qr,
        "expiry_time": time
    })

# @api_view(["POST"])
# def check_timer(request):
#     is_expired=request.data.get("is_expired")
#     session_id=request.data.get("session_id")
#     if is_expired:
#         cache.delete(f"qr_session_{session_id}")
#         return JsonResponse({"message": "session deleted"},status=200)
#     return JsonResponse({"message": "session not deleted"},status=500)

@api_view(["POST"])
def mobile_upload(request, session_id):
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file detected"}, status=400)

        #validation
    session_exists = cache.get(f"qr_session_mobile_{session_id}")
    if not session_exists:
        return JsonResponse({"error": "Invalid or expired QR code session (PC disconnected or timeout)"}, status=403)

    

    uploaded_file = request.FILES['file']

    try:
      

        # BLOB MISSING 
        #db check if for that session we have something
        if(Files.objects.filter(session_id=session_id).exists()):
            return JsonResponse({"error": "session already used"}, status=400)

        file_instance = Files.objects.create(
        session_id=session_id,
        file=uploaded_file,
        user_id=user_id 
        )
    full_file_url = request.build_absolute_uri(file_instance.file.url)
    channel_layer = get_channel_layer() 
    async_to_sync(channel_layer.group_send)(
        f"transfer_{session_id}",
        {
            "type": "send_file_notification",
            "status": "uploaded",
            "file_url": full_file_url,
            "file_name": uploaded_file.name
        }
    )
      
        # Delete sessions after successful upload (Single Use)
        cache.delete(f"qr_session_pc_{session_id}")
        cache.delete(f"qr_session_mobile_{session_id}")
        
        return JsonResponse({"message": "File sent to PC!", "location": full_file_url})
   
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






    
    

    

    

  