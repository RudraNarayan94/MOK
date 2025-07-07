from celery import shared_task
from .utils import update_daily_statistics, update_all_time_statistics

@shared_task
def update_daily_statistics_task(user_id):
    from accounts.models import User
    user = User.objects.get(id=user_id)
    update_daily_statistics(user)

@shared_task
def update_all_time_statistics_task(user_id):
    from accounts.models import User
    user = User.objects.get(id=user_id)
    update_all_time_statistics(user)
