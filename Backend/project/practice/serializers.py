from rest_framework import serializers
from .models import *

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "user", "total_time", "lessons_completed",
            "top_speed", "avg_speed", "top_accuracy", "avg_accuracy"
        ]

class PracticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeSession
        fields = [
            "id", "user", "speed", "accuracy", "time_taken", "errors", "timestamp"
        ]
        read_only_fields = ["id", "timestamp"]

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

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Leaderboard
        fields = [
            "user", "rank", "wpm", "accuracy", "updated_at"
        ]
