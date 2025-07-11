from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class PracticeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'practice'

    def ready(self):
        from django.conf import settings

        # if settings.CELERY_TASK_ALWAYS_EAGER:  # optional: prevent loop during testing
        #     return
        

        try:
            # Import here to avoid circular import issues
            from .tasks import ingest_paragraphs_from_csv
            ingest_paragraphs_from_csv.delay()
            logger.info("Triggered CSV ingestion via Celery.")
        except Exception as e:
            logger.error(f"Failed to trigger paragraph ingestion: {e}")
