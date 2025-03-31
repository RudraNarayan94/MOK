from django.urls import path
from .views import *

urlpatterns = [
  path('sessions/', PracticeSessionView.as_view(), name='sessions'),
]