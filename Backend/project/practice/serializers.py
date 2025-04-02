from rest_framework import serializers
from .models import PracticeSession

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = ['time_taken', 'speed', 'accuracy']

        
