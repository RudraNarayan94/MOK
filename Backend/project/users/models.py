from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_img = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    current_streak = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(default=now)  # Auto-updated on activity
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"  # Users will log in with email instead of username
    REQUIRED_FIELDS = ["username"]  # Username is collected after OAuth login

    def __str__(self):
        return self.username


class UserPerformance(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="performance")
    date = models.DateField(default=now)
    wpm = models.FloatField()
    accuracy = models.FloatField()
    duration_seconds = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.wpm} WPM on {self.date}"

# class ContestParticipant(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="contest_participations")
#     contest_name = models.CharField(max_length=255)
#     date = models.DateField(default=now)
#     wpm = models.FloatField()
#     accuracy = models.FloatField()
#     rank = models.PositiveIntegerField()

#     def __str__(self):
#         return f"{self.user.username} - {self.contest_name} - Rank {self.rank}"
