from rest_framework.decorators import api_view
from django.http import JsonResponse
from apps.qr.interactors.generate_qr_interactor import GenerateQrInteractor   
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response

class QRViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def generate(self, request):
        result = GenerateQrInteractor.execute()
        return Response(result)