from django.db import models
from accounts.models import User

# Create your models here.
class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="practice_sessions")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    time_taken = models.PositiveIntegerField()  # in ms or s
    text_length = models.PositiveIntegerField()  # total characters in the test
    errors = models.PositiveIntegerField(default=0)  # total mistakes
    speed = models.FloatField()  # WPM
    accuracy = models.FloatField()  # accuracy percentage

    def __str__(self):
        return f"{self.user.username} session at {self.timestamp}"
