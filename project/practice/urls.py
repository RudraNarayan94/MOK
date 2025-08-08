from django.urls import path
from .views import *

urlpatterns = [
    path('texts/', TextSnippetView.as_view(), name='texts'),
    path('sessions/', PracticeSessionView.as_view(), name='sessions'),
    path('daily_stats/', DailyStatisticsView.as_view(), name='daily_stats'),
    path('all_time_stats/', AllTimeStatisticsView.as_view(), name='all_time_stats'),
    path('streak/', StreakView.as_view(), name='streak'),
    path('user_rank/', UserRankView.as_view(), name='user_rank'),
    path('graph/', GraphDataView.as_view(), name='graph'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]