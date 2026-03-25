from rest_framework.decorators import api_view
from django.http import JsonResponse
from qr.interactors.generate_qr_interactor import GenerateQrInteractor   


@api_view(["GET"])
def generate_qr(request):
   result = GenerateQrInteractor.execute()
   return JsonResponse(result)


# @api_view(["POST"])

# def mobile_upload(request, room_id):
 
   

#     session_active = cache.get(f"qr_session_active_{room_id}")
#     room_exists = cache.get(f"qr_session_count_{room_id}")

#     if not session_active:
#         if room_exists is not None:
        
#             return JsonResponse({"error": "PC is still connecting. Retrying..."}, status=403)
#         else:
           
#             return JsonResponse({"error": "QR code has expired or is invalid."}, status=410)
    
#     uploaded_file = request.FILES.get('file')

#     if uploaded_file is None:
      
#         return JsonResponse({"error": "No file detected"}, status=400)
    
#     #file validation
#     ext = os.path.splitext(uploaded_file.name)[1].lower()
#     if ext not in allowed_file_types:
#         return JsonResponse({"error": "File type not allowed"}, status=400)
#     if uploaded_file.content_type not in allowed_mime_types:
#         return JsonResponse({"error": "File type not allowed"}, status=400)

#     if uploaded_file.size > allowed_file_size:
#         return JsonResponse({"error": "File too large. Max size is 25MB."}, status=400)

#     #from token
#     user_id = 1

#     try:
#         #blob missing
#         # also add db validation

#         file_instance = Files.objects.create(
#             session_id=room_id,
#             file=uploaded_file,
#             user_id=user_id 
#         )
#         full_file_url = request.build_absolute_uri(file_instance.file.url)
#         channel_layer = get_channel_layer() 
#         async_to_sync(channel_layer.group_send)(
#             #room name
#             f"transfer_{room_id}",
#             {
#                 "type": "send_file_notification",
#                 "status": "uploaded",
#                 "file_url": full_file_url,
#                 "file_name": uploaded_file.name,
#                 "method":"mobile"
#             }
#         )
#         cache.delete(f"qr_session_active_{room_id}")
#         cache.delete(f"qr_session_count_{room_id}")

#         return JsonResponse({"message": "File sent to PC!"},status=200)
   
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)






    
    

    

    

  