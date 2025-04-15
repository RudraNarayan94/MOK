from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from accounts.renderers import UserRenderer

class RoomCreateView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = RoomSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        room = serializer.save()
        return Response({'code': room.code}, status=status.HTTP_201_CREATED)

class RoomJoinView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, code, format=None):
        try:
            room = Room.objects.get(code=code, is_active=True)
        except Room.DoesNotExist:
            return Response(
                {"detail": "Room not found or is no longer active."},
                status=status.HTTP_404_NOT_FOUND
            )

        participant, created = Participant.objects.get_or_create(room=room, user=request.user)
        # if not created:
        #     return Response(
        #         {"detail": "You have already joined this room."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        

        return Response(
            {"msg": f"Joined room {code} successfully."},
            status=status.HTTP_200_OK
        )

            


