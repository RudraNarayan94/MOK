from django.urls import path
from .views import *

urlpatterns = [
    path('rooms/', RoomCreateView.as_view(), name='room-create'),
    path('rooms/<str:code>/join/', RoomJoinView.as_view(), name='room-join'),
    path('rooms/<str:code>/text/', RoomTextView.as_view(), name='room-text'),
    path('rooms/<str:code>/results/', RoomResultView.as_view(), name='room-results'),
    path('rooms/<str:code>/leaderboard/', RoomLeaderboardView.as_view(), name='room-leaderboard'),
]
