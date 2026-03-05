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

@api_view(["GET"])
def gen_qr(request):
    session_id = generate_session_id()
    qr = get_qr(session_id)

    # from token get user id
    user_id = 1
    cache.set(f"qr_session_{session_id}", user_id, timeout=600) 

    return JsonResponse({
        "session_id": session_id,
        "qr_code": qr
    })

@api_view(["GET"])
def ping(request):
    return JsonResponse({"message": "Pong! Connection completely successful."})

@api_view(["POST"])
def mobile_upload(request, session_id):
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file detected"}, status=400)
        

    user_id = cache.get(f"qr_session_{session_id}")

    # missing check between acutal user id and id in cache



    
    if not user_id:
        return JsonResponse({"error": "Invalid or expired QR code session"}, status=403)

    uploaded_file = request.FILES['file']

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
    cache.delete(f"qr_session_{session_id}")

    return JsonResponse({"message": "File sent to PC!","location":full_file_url})

    









    
    

    

    

  