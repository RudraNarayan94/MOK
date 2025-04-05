from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from .models import *
from accounts.renderers import UserRenderer
from django.db.models import Sum, Avg, Max, Count
from django.utils import timezone
from datetime import timedelta


class PracticeSessionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  

    def post(self, request, format=None):
        serializer = PracticeSessionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response({"msg": "session recorded successfully"}, status=status.HTTP_201_CREATED)


   
class DailyStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  

    def get(self, request, format=None):
        today = timezone.now().date()
        sessions = PracticeSession.objects.filter(user=request.user, timestamp__date=today)

        if not sessions.exists():
            return Response({"detail": "No sessions today"}, status=status.HTTP_404_NOT_FOUND)

        try:
            agg = sessions.aggregate(
                total_time=Sum('time_taken'),
                lessons_completed=Count('id'),
                top_speed=Max('speed'),
                avg_speed=Avg('speed'),
                top_accuracy=Max('accuracy'),
                avg_accuracy=Avg('accuracy'),
            )
            agg['total_time'] = int(agg['total_time'] / 1000)  # ms → s
            serializer = DailyStatisticsSerializer(agg)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Unable to retrieve daily statistics. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class AllTimeStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  

    def get(self, request, format=None):
        if not DailyStatistics.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "No data available."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            stats = DailyStatistics.objects.filter(user=request.user).aggregate(
                total_time=Sum('total_time'),
                lessons_completed=Sum('lessons_completed'),
                top_speed=Max('top_speed'),
                avg_speed=Avg('avg_speed'),
                top_accuracy=Max('top_accuracy'),
                avg_accuracy=Avg('avg_accuracy'),
            )
            serializer = AllTimeStatisticsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Unable to compute all-time statistics."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StreakView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        try:
            streak = 0
            day = timezone.now().date()

            while PracticeSession.objects.filter(user=request.user, timestamp__date=day).exists():
                streak += 1
                day -= timedelta(days=1)
            serializer = StreakSerializer({"current_streak": streak})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Unable to calculate streak. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LeaderboardView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]
    
    def get(self, request, format=None):
        users = User.objects.filter(practice_sessions__isnull=False).distinct()
        if not users.exists():
            return Response(
                {"detail": "No leaderboard data available."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            leaderboard = []
            for u in users:
                best = PracticeSession.objects.filter(user=u).aggregate(best_wpm=Max('speed'))['best_wpm'] or 0
                leaderboard.append({"username": u.username, "best_wpm": best})

            top10 = sorted(leaderboard, key=lambda x: x['best_wpm'], reverse=True)[:10]
            serializer = LeaderboardEntrySerializer(top10, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Unable to load leaderboard. Please refresh later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )