from django.apps import AppConfig


class DataProcessorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_processor'

    def ready(self):
        # This is necessary in order to auto discover tasks
        from .tasks import task_process_csv
