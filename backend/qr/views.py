from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .helper import generate_room_id,get_qr
from rest_framework.decorators import api_view
from .models import Files
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache


@api_view(["GET"])
def generate_qr(request):
    room_id = generate_room_id()
    qr = get_qr(room_id)

    # from token get user id
    user_id = request.get('user_id')
    time=30
        
 

    return JsonResponse({
        "room_id": room_id,
        "qr_code": qr,
        "expiry_time": time
    })


@api_view(["POST"])
def mobile_upload(request, room_id):
    if 'file' not in request.FILES:
        return JsonResponse({"error": "No file detected"}, status=400)

    
    session_exists = cache.get(f"qr_session_mobile_{room_id}")
    if not session_exists:
        return JsonResponse({"error": "Invalid or expired QR code session (PC disconnected or timeout)"}, status=403)
        
    user_id = 1
    uploaded_file = request.FILES['file']
    try:
        #blob missing

        file_instance = Files.objects.create(
            session_id=room_id,
            file=uploaded_file,
            user_id=user_id 
        )
        full_file_url = request.build_absolute_uri(file_instance.file.url)
        channel_layer = get_channel_layer() 
        async_to_sync(channel_layer.group_send)(
            #room name
            f"transfer_{room_id}",
            {
                "type": "send_file_notification",
                "status": "uploaded",
                "file_url": full_file_url,
                "file_name": uploaded_file.name
            }
        )
      
        cache.delete(f"qr_session_pc_{room_id}")
        cache.delete(f"qr_session_mobile_{room_id}")
        
        return JsonResponse({"message": "File sent to PC!"},status=200)
   
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






    
    

    

    

  