from rest_framework import serializers
from .models import *

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = ["id", "user", "speed", "accuracy", "time_taken", "timestamp"]
        read_only_fields = ["timestamp"]

    def create(self, validated_data):
        session = PracticeSession.objects.create(**validated_data)
        return session
    
class DailyStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStatistics
        fields = [
            "date", "total_time", "lessons_completed",
            "top_speed", "avg_speed", "top_accuracy", "avg_accuracy"
        ]
class AllTimeStatisticsSerializer(serializers.Serializer):
    total_time = serializers.IntegerField()
    lessons_completed = serializers.IntegerField()
    top_speed = serializers.FloatField()
    avg_speed = serializers.FloatField()
    top_accuracy = serializers.FloatField()
    avg_accuracy = serializers.FloatField()



class StreakSerializer(serializers.Serializer):
    current_streak = serializers.IntegerField()

class LeaderboardEntrySerializer(serializers.Serializer):
    username = serializers.CharField()
    best_wpm = serializers.FloatField()
