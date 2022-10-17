from unittest import mock

import factory.django
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework import status

from core.helpers.api.tests import APITestBase
from data_processor.factories import CSVTaskFactory
from data_processor.models import CSVTask


class ProcessFileViewTest(APITestBase):
    url = reverse('data_processor:process_file')

    def test_post_file_previously_processed_409_CONFLICT(self):
        initial_input_file_name = 'test_file.csv'
        previous_csv_task: CSVTask = CSVTaskFactory(initial_input_file_name=initial_input_file_name)
        data_to_send = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        self.assertEqual(CSVTask.objects.count(), 1)
        response = self.client.post(self.url, data=data_to_send)
        self.assertEqual(CSVTask.objects.count(), 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_409_CONFLICT
        )
        self.assertEqual(
            response.data['uuid'],
            previous_csv_task.uuid.hex
        )

    def test_post_201_CREATED(self):
        initial_input_file_name = 'test.csv'
        data_to_send = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        self.assertEqual(CSVTask.objects.count(), 0)
        response = self.client.post(self.url, data=data_to_send)
        self.assertEqual(CSVTask.objects.count(), 1)
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        csv_task: CSVTask = CSVTask.objects.last()
        self.assertEqual(
            response.data,
            {
                'uuid': csv_task.uuid.hex,
            }
        )
        csv_task.initial_input_file_name = initial_input_file_name


class CSVTaskView(APITestBase):
    url = reverse('data_processor:csv_task_result', kwargs={'uuid': None})

    def test_not_processed_425_TOO_EARLY(self):
        csv_task: CSVTask = CSVTaskFactory()
        url = reverse('data_processor:csv_task_result', kwargs={'uuid': csv_task.uuid.hex})
        with mock.patch.object(
            CSVTask, 'processed', new_callable=mock.PropertyMock
        ) as mock_processed:
            mock_processed.return_value = False
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                425
            )
            self.assertEqual(mock_processed.call_count, 1)

    def test_processed_200_OK(self):
        csv_task: CSVTask = CSVTaskFactory(output_files__total=1)
        url = reverse('data_processor:csv_task_result', kwargs={'uuid': csv_task.uuid.hex})
        with mock.patch.object(
            CSVTask, 'processed', new_callable=mock.PropertyMock
        ) as mock_processed:
            mock_processed.return_value = True
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK
            )
            self.assertEqual(mock_processed.call_count, 1)
