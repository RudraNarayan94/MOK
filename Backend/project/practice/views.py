from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from accounts.renderers import UserRenderer


class PracticeSessionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  

    def post(self, request, format=None):
        serializer = PracticeSessionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"msg": "Session recorded successfully"}, status=status.HTTP_201_CREATED)
