from .models import PracticeSession, DailyStatistics, AllTimeStatistics
from django.utils import timezone
from django.db.models import Avg, Max, Sum, Count


def update_daily_statistics(user):
    today = timezone.now().date()
    sessions = PracticeSession.objects.filter(user=user, timestamp__date=today)

    if not sessions.exists():
        return

    agg = sessions.aggregate(
        total_time=Sum('time_taken'),
        lessons_completed=Count('id'),
        top_speed=Max('speed'),
        avg_speed=Avg('speed'),
        top_accuracy=Max('accuracy'),
        avg_accuracy=Avg('accuracy'),
    )

    agg['total_time'] = int((agg['total_time'] or 0) / 1000)  # ms → s

    stats, _ = DailyStatistics.objects.get_or_create(user=user, date=today)
    stats.total_time = agg['total_time']
    stats.lessons_completed = agg['lessons_completed'] or 0
    stats.top_speed = agg['top_speed'] or 0
    stats.avg_speed = agg['avg_speed'] or 0
    stats.top_accuracy = agg['top_accuracy'] or 0
    stats.avg_accuracy = agg['avg_accuracy'] or 0
    stats.save()


def update_all_time_statistics(user):
    try:
        daily_stats = DailyStatistics.objects.filter(user=user)

        if not daily_stats.exists():
            return  

        agg = daily_stats.aggregate(
            total_time_spent=Sum('total_time'),
            total_lessons_completed=Sum('lessons_completed'),
            top_speed=Max('top_speed'),
            avg_speed=Avg('avg_speed'),
            top_accuracy=Max('top_accuracy'),
            avg_accuracy=Avg('avg_accuracy'),
        )

        profile, _ = AllTimeStatistics.objects.get_or_create(user=user)

        profile.total_time_spent = agg["total_time_spent"] or 0
        profile.total_lessons_completed = agg["total_lessons_completed"] or 0
        profile.top_speed = agg["top_speed"] or 0
        profile.avg_speed = agg["avg_speed"] or 0
        profile.top_accuracy = agg["top_accuracy"] or 0
        profile.avg_accuracy = agg["avg_accuracy"] or 0

        profile.save()

    except Exception as e:
        print(f"Error updating all-time stats: {e}")
