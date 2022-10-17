from logging import Logger
from unittest import mock

import factory
from django.core.files.base import ContentFile
from django.db import transaction
from django.test import TestCase

from data_processor.factories import CSVTaskFileFactory, CSVTaskFactory
from data_processor.models import CSVTask


class CSVTaskFileTest(TestCase):

    def test_str(self):
        file_name = 'test_file.csv'
        test_file = ContentFile(
            factory.django.FileField()._make_data(
                {'data': b'test_content'}
            ),
            file_name
        )
        csv_task_with_file = CSVTaskFileFactory(output_file=test_file)
        csv_task_without_file = CSVTaskFileFactory(output_file=None)
        test_data_list = [
            (csv_task_with_file, csv_task_with_file.output_file.name),
            (csv_task_without_file, 'No file')
        ]
        for test_data in test_data_list:
            with self.subTest(
                test_data=test_data
            ):
                csv_task_file, expected = test_data
                self.assertEqual(str(csv_task_file), expected)


class CSVTaskTest(TestCase):
    def test_processed(self):
        csv_task_with_output_files: CSVTask = CSVTaskFactory(output_files__total=1)
        csv_task_without_output_files: CSVTask = CSVTaskFactory(output_files__total=0)
        test_data_list = [
            (csv_task_with_output_files, True),
            (csv_task_without_output_files, False),
        ]
        for test_data in test_data_list:
            with self.subTest(test_data=test_data):
                csv_task, expected = test_data
                self.assertEqual(csv_task.processed, expected)

    def test_process(self):

        test_data_list = [
            (True, False, 1, 0),
            (False, True, 0, 1),
        ]
        for test_data in test_data_list:
            with mock.patch.object(
                CSVTask, 'processed', new_callable=mock.PropertyMock
            ) as mock_processed, mock.patch(
                'data_processor.tasks.process_csv.task_process_csv.delay'
            ) as mock_task_process, mock.patch.object(
                Logger, 'warning'
            ) as mock_logger, self.subTest(
                test_data=test_data
            ), transaction.atomic():
                csv_task: CSVTask = CSVTaskFactory()
                processed, expected, mock_logger_call_count, mock_task_process_call_count = test_data
                mock_processed.return_value = processed
                self.assertEqual(csv_task.process(), expected)
                self.assertEqual(mock_logger.call_count, mock_logger_call_count)
                self.assertEqual(mock_task_process.call_count, mock_task_process_call_count)
                transaction.set_rollback(True)
