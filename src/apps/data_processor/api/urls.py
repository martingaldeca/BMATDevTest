from django.urls import path
from data_processor.api import views as data_processor_views

app_name = 'core'

urlpatterns = [
    path('process_file/', data_processor_views.ProcessFileView.as_view(), name='process_file'),
    path('csv_task_result/<uuid>/', data_processor_views.CSVTaskView.as_view(), name='csv_task_result'),
]
