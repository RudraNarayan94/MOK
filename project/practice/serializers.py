from rest_framework import serializers
from .models import *

class TextSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextSnippet
        fields = ['index', 'content']
class PracticeSessionSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = PracticeSession
        fields = [
            'user',
            'time_taken',
            'speed',
            'accuracy',
        ]
        read_only_fields = ["user","timestamp"]

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
class AllTimeStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllTimeStatistics
        fields = [
            "total_time_spent","total_lessons_completed","top_speed",
            "avg_speed", "top_accuracy","avg_accuracy"
        ]



class StreakSerializer(serializers.Serializer):
    current_streak = serializers.IntegerField()


