from rest_framework import serializers
from .models import Room, Participant
from .utils import generate_unique_room_code
class RoomSerializer(serializers.ModelSerializer):
    host = serializers.HiddenField(default=serializers.CurrentUserDefault())
    code = serializers.CharField(read_only=True)

    class Meta:
        model = Room
        fields = ['code', 'text', 'host']

    def create(self, validated_data):
        code = generate_unique_room_code()
        validated_data['code'] = code
        return super().create(validated_data)


class ParticipantResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['wpm', 'accuracy']


class LeaderboardEntrySerializer(serializers.Serializer):
    username = serializers.CharField()
    wpm = serializers.FloatField()
    accuracy = serializers.FloatField()
    finished_at = serializers.DateTimeField()
