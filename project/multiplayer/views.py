from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.renderers import UserRenderer
from django.utils import timezone
from django.core.cache import cache

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
    
class RoomTextView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, code, format=None):
        cache_key = f"room_text:{code}"
        cached_text = cache.get(cache_key)
        if cached_text:
            return Response({'text': cached_text}, status=status.HTTP_200_OK)

        try:
            room = Room.objects.get(code=code)
        except Room.DoesNotExist:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        cache.set(cache_key, room.text, timeout=300)
        return Response({'text': room.text}, status=status.HTTP_200_OK)
            
class RoomResultView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, code, format=None):
        try:
            room = Room.objects.get(code=code)
        except Room.DoesNotExist:
            return Response(
                {"detail": "Room not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            participant = Participant.objects.get(room=room, user=request.user)
        except Participant.DoesNotExist:
            return Response(
                {"detail": "You are not a participant in this room."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ParticipantResultSerializer(participant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(finished_at=timezone.now())

        return Response(
            {"msg": "Your result has been recorded."},
            status=status.HTTP_200_OK
        )

class RoomLeaderboardView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def get(self, request, code, format=None):
        cache_key = f"room_leaderboard:{code}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        try:
            room = Room.objects.get(code=code)
        except Room.DoesNotExist:
            return Response({"detail": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        participants = Participant.objects.filter(
            room=room, wpm__isnull=False
        ).order_by('-wpm')

        if not participants.exists():
            return Response({"detail": "No results submitted yet."}, status=status.HTTP_404_NOT_FOUND)

        data = [
            {
                "username": p.user.username,
                "wpm": p.wpm,
                "accuracy": p.accuracy,
                "finished_at": p.finished_at
            }
            for p in participants
        ]

        serializer = LeaderboardEntrySerializer(data, many=True)
        cache.set(cache_key, serializer.data, timeout=120)
        return Response(serializer.data, status=status.HTTP_200_OK)
