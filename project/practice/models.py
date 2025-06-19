from django.db import models
from accounts.models import User

# Create your models here.
class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="practice_sessions")
    timestamp = models.DateTimeField(auto_now_add=True)

    time_taken = models.PositiveIntegerField()  # in ms or s
    speed = models.FloatField()  
    accuracy = models.FloatField()  

    # text_length = models.PositiveIntegerField()  # total characters in the test
    # errors = models.PositiveIntegerField(default=0)  # total mistakes

    def __str__(self):
        return f"{self.user.username} session at {self.timestamp}"
    
class DailyStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_statistics")
    date = models.DateField(auto_now_add=True)
    
    total_time = models.PositiveIntegerField(default=0)  # in seconds
    lessons_completed = models.PositiveIntegerField(default=0)
    top_speed = models.FloatField(default=0)
    avg_speed = models.FloatField(default=0)
    top_accuracy = models.FloatField(default=0)
    avg_accuracy = models.FloatField(default=0)

    class Meta:
      constraints = [
          models.UniqueConstraint(fields=['user', 'date'], name='unique_user_date')
      ]

    def __str__(self):
        return f"{self.user.username} -> {self.date}"


class AllTimeStatistics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    total_time_spent = models.PositiveIntegerField(default=0)  
    total_lessons_completed = models.PositiveIntegerField(default=0)
    top_speed = models.FloatField(default=0)  
    avg_speed = models.FloatField(default=0)
    top_accuracy = models.FloatField(default=0)  
    avg_accuracy = models.FloatField(default=0)
    
    def __str__(self):
        return self.user.username
    
# class Leaderboard(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     rank = models.PositiveIntegerField(unique=True)  
#     speed = models.FloatField()  
#     accuracy = models.FloatField()  
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.rank}. {self.user.username}"
