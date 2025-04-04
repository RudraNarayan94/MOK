from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from accounts.renderers import UserRenderer
from django.db.models import Sum, Avg, Max
from django.utils import timezone


class PracticeSessionView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [UserRenderer]  

    def post(self, request, format=None):
        serializer = PracticeSessionSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        session = serializer.save(user=request.user)
        self.update_daily_statistics(session)
        return Response({"msg": "session recorded successfully"}, status=status.HTTP_201_CREATED)


    def update_daily_statistics(self, session):
        today = timezone.now().date()
        user = session.user

        today_stats, created = DailyStatistics.objects.get_or_create(user=user, date=today)
        sessions = PracticeSession.objects.filter(user=user, timestamp__date=today) 

        agg = sessions.aggregate(
            total_time = Sum('time_taken'),
            top_speed = Max('speed'),
            avg_speed = Avg('speed'),
            top_accuracy = Max('accuracy'),
            avg_accuracy = Avg('accuracy')
        )

        today_stats.total_time = int((agg.get('total_time') or 0) / 1000) # converting ms to sec
        today_stats.lessons_completed = sessions.count()
        today_stats.top_speed = agg.get('top_speed') or 0
        today_stats.avg_speed = agg.get('avg_speed') or 0
        today_stats.top_accuracy = agg.get('top_accuracy') or 0
        today_stats.avg_accuracy = agg.get('avg_accuracy') or 0

        today_stats.save()

class DailyStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        today = timezone.now().date()
        try:
            daily_stats = DailyStatistics.objects.get(user=request.user, date=today)
        except DailyStatistics.DoesNotExist:
            return Response({"msg": "No statistics available for today"}, status=status.HTTP_404_NOT_FOUND)
        serializer = DailyStatisticsSerializer(daily_stats)
        return Response(serializer.data, status=status.HTTP_200_OK)