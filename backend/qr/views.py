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

    
   
    cache.add(f"qr_session_count_{room_id}", 0, timeout=30*60)

 
    user_id = request.query_params.get('user_id')
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

    session_active = cache.get(f"qr_session_active_{room_id}")
    room_exists = cache.get(f"qr_session_count_{room_id}")

    if not session_active:
        if room_exists is not None:
        
            return JsonResponse({"error": "PC is still connecting. Retrying..."}, status=403)
        else:
           
            return JsonResponse({"error": "QR code has expired or is invalid."}, status=410)
        
   
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
        cache.delete(f"qr_session_active_{room_id}")
        cache.delete(f"qr_session_count_{room_id}")

        return JsonResponse({"message": "File sent to PC!"},status=200)
   
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






    
    

    

    

  