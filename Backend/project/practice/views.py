from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from .models import *
from accounts.renderers import UserRenderer
from django.utils import timezone
from datetime import timedelta
from .utils import update_daily_statistics, update_all_time_statistics

class PracticeSessionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = PracticeSessionSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
            session = serializer.save(user=request.user)

            # updates
            update_daily_statistics(request.user)
            update_all_time_statistics(request.user)

            return Response({"msg": "Session recorded successfully."}, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response(
                {"detail": "Invalid session data. Please check your input.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception:
            return Response(
                {"detail": "Something went wrong while recording the session. Try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



   
class DailyStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        today = timezone.now().date()
        try:
            stats = DailyStatistics.objects.get(user=request.user, date=today)
        except DailyStatistics.DoesNotExist:
            return Response(
                {"detail": "No daily stats found for today."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DailyStatisticsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

  
class AllTimeStatisticsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        try:
            stats = AllTimeStatistics.objects.get(user=request.user)
            serializer = AllTimeStatisticsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AllTimeStatistics.DoesNotExist:
            return Response(
                {"detail": "All-time statistics not available for this user."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {"detail": "Unable to load all-time statistics. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StreakView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        try:
            streak = 0
            day = timezone.now().date()

            while DailyStatistics.objects.filter(user=request.user, date=day).exists():
                streak += 1
                day -= timedelta(days=1)

            serializer = StreakSerializer({"current_streak": streak})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Unable to fetch streak stats right now, try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserRankView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        stats_qs = AllTimeStatistics.objects.filter(top_speed__gt=0).order_by('-top_speed')
        total = stats_qs.count()
        try:
            position = list(stats_qs.values_list('user_id', flat=True)).index(request.user.id) + 1
        except ValueError:
            return Response({"detail": "No typing data."}, status=status.HTTP_404_NOT_FOUND)

        percentile = round((total - position) / total * 100, 2)
        # Optionally save to profile
        profile = request.user.userprofile
        profile.world_rank = position
        profile.rank_percentile = percentile
        profile.save(update_fields=['world_rank', 'rank_percentile'])

        return Response({"world_rank": position, "rank_percentile": percentile})


class LeaderboardView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [UserRenderer]

    def get(self, request, format=None):
        sort_by = request.query_params.get("sort_by", "top_speed")

        if sort_by not in ["top_speed", "avg_speed"]:
            return Response(
                {"detail": "Invalid parameter. Use 'sort_by=top_speed' or 'sort_by=avg_speed'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        stats_qs = AllTimeStatistics.objects.filter(**{f"{sort_by}__gt": 0}).order_by(f"-{sort_by}")[:10]

        if not stats_qs.exists():
            return Response(
                {"detail": f"No leaderboard data found for '{sort_by}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = [
            {
                "username": stat.user.username,
                "wpm": getattr(stat, sort_by)
            }
            for stat in stats_qs
        ]
        return Response(data, status=status.HTTP_200_OK)

