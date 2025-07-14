import csv
import os
from django.conf import settings
from .models import TextSnippet
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



@shared_task
def ingest_paragraphs_from_csv():
    csv_path = os.path.join(settings.BASE_DIR, 'data', 'paragraphs.csv')

    if not os.path.exists(csv_path):
        print("❌ CSV file not found!")
        return

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        inserted = 0
        for row in reader:
            index = int(row["index"])
            content = row["paragraph"]

            if not TextSnippet.objects.filter(index=index).exists():
                TextSnippet.objects.create(index=index, content=content)
                inserted += 1

    print(f"✅ CSV Ingestion Complete: {inserted} new snippets added.")
