from logging import Logger
from unittest import mock

from django.db import transaction
from django.test import TestCase

from data_processor.factories import CSVTaskFactory
from data_processor.models import CSVTask
from data_processor.tasks.process_csv import process_csv


class ProcessCsvTest(TestCase):

    def test_process_csv(self):
        test_files = [
            '/src/apps/data_processor/tasks/tests/test_csvs/initial_test.csv',
            '/src/apps/data_processor/tasks/tests/test_csvs/initial_test_without_headers.csv',
        ]
        for test_file in test_files:
            with mock.patch.object(
                Logger, 'info'
            ) as mock_logger, self.subTest(
                test_file=test_file
            ), transaction.atomic():
                csv_task: CSVTask = CSVTaskFactory(output_files__total=0)
                process_csv(
                    task_uuid=csv_task.uuid.hex,
                    csv_path=test_file
                )
                self.assertEqual(mock_logger.call_count, 3)
                csv_task.refresh_from_db()
                self.assertEqual(csv_task.output_files.count(), 1)
                self.assertEqual(
                    set(csv_task.output_files.last().output_file.readlines()),
                    {
                        b'Song,Date,Number of Plays\n',
                        b'In The End,2020-01-01,1500\n',
                        b'In The End,2020-01-02,500\n',
                        b'Umbrella,2020-01-01,150\n',
                        b'Umbrella,2020-01-02,250\n'
                    }
                )
                transaction.set_rollback(True)

    def test_process_check_format_fails(self):
        test_data_list = [
            (
                '/src/apps/data_processor/tasks/tests/test_csvs/initial_test_with_not_valid_headers.csv',
                ValueError,
                'not valid headers'
            ),
            (
                '/src/apps/data_processor/tasks/tests/test_csvs/initial_test_with_invalid_value.csv',
                TypeError,
                'Number of Plays must be of type int. The file is corrupted. Unable to parse string "patata" at '
                'position 2'
            ),
        ]
        for test_data in test_data_list:
            with self.subTest(test_data=test_data), mock.patch.object(
                Logger, 'exception'
            ) as mock_logger_exception, transaction.atomic():
                csv_path, error, expected_message = test_data
                with self.assertRaises(error) as expected_exception:
                    csv_task: CSVTask = CSVTaskFactory(output_files__total=0)
                    process_csv(
                        task_uuid=csv_task.uuid.hex,
                        csv_path=csv_path
                    )
                self.assertEqual(str(expected_exception.exception), expected_message)
                self.assertEqual(mock_logger_exception.call_count, 1)
                csv_task.refresh_from_db()
                self.assertEqual(csv_task.output_files.count(), 0)
                self.assertTrue(csv_task.error_processing)
                self.assertEqual(csv_task.error_message, str(expected_exception.exception))
                transaction.set_rollback(True)
