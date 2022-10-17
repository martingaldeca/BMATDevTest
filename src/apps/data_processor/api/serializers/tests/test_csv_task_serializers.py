from unittest import mock

import factory
from django.core.files.base import ContentFile

from core.helpers.api.tests import SerializerTestBase
from core.exceptions import api as api_exceptions
from data_processor.api.serializers import ProcessFileSerializer, CSVTaskFileSerializer, CSVTaskSerializer
from data_processor.factories import CSVTaskFactory, CSVTaskFileFactory
from data_processor.models import CSVTask, CSVTaskFile


class ProcessFileSerializerTest(SerializerTestBase):

    def test_data(self):
        csv_task: CSVTask = CSVTaskFactory()
        expected_data = {
            'uuid': csv_task.uuid.hex,
        }
        self.assertEqual(ProcessFileSerializer(instance=csv_task).data, expected_data)

    def test_validate_file_exists_409_CONFLICT(self):
        initial_input_file_name = 'test_file.csv'
        previous_csv_task: CSVTask = CSVTaskFactory(initial_input_file_name=initial_input_file_name)
        in_data = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        serializer = ProcessFileSerializer(data=in_data)
        with self.assertRaises(api_exceptions.ConflictException) as expected_exception:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            expected_exception.exception.detail['uuid'],
            previous_csv_task.uuid.hex
        )

    def test_validate_file_does_not_exists_OK(self):
        initial_input_file_name = 'test_file.csv'
        in_data = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        serializer = ProcessFileSerializer(data=in_data)
        self.assertIsNone(serializer.context.get('initial_input_file_name'))
        serializer.is_valid(raise_exception=True)
        self.assertEqual(
            serializer.context['initial_input_file_name'],
            initial_input_file_name
        )

    def test_save_previously_processed_412_PRECONDITION_FAILED(self):
        initial_input_file_name = 'test_file.csv'
        in_data = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        with mock.patch.object(
            CSVTask, 'process'
        ) as mock_process, self.assertRaises(
            api_exceptions.PreconditionFailedException
        ) as expected_exception:
            mock_process.return_value = False
            serializer = ProcessFileSerializer(data=in_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        previous_csv_task = CSVTask.objects.last()
        self.assertEqual(mock_process.call_count, 1)
        self.assertEqual(
            expected_exception.exception.detail['uuid'],
            previous_csv_task.uuid.hex
        )

    def test_save_OK(self):
        initial_input_file_name = 'test_file.csv'
        in_data = {
            'file': ContentFile(
                factory.django.FileField()._make_data(
                    {'data': b'test_content'}
                ),
                initial_input_file_name
            )
        }
        with mock.patch.object(
            CSVTask, 'process'
        ) as mock_process:
            mock_process.return_value = True
            serializer = ProcessFileSerializer(data=in_data)
            serializer.is_valid(raise_exception=True)
            csv_task = serializer.save()
            self.assertEqual(mock_process.call_count, 1)
            self.assertEqual(csv_task.initial_input_file_name, initial_input_file_name)


class CSVTaskFileSerializerTest(SerializerTestBase):
    def test_data(self):
        csv_task_file: CSVTaskFile = CSVTaskFileFactory()
        expected_data = {
            'uuid': csv_task_file.uuid.hex,
            'output_file': csv_task_file.output_file.url
        }
        self.assertEqual(CSVTaskFileSerializer(instance=csv_task_file).data, expected_data)


class CSVTaskSerializerTest(SerializerTestBase):

    def test_data_not_processed_425_TOO_EARLY(self):
        csv_task: CSVTask = CSVTaskFactory()
        with mock.patch.object(
            CSVTask, 'processed', new_callable=mock.PropertyMock
        ) as mock_processed, self.assertRaises(
            api_exceptions.TooEarlyException
        ) as expected_exception:
            mock_processed.return_value = False
            _ = CSVTaskSerializer(instance=csv_task).data
        self.assertEqual(mock_processed.call_count, 1)
        self.assertEqual(
            expected_exception.exception.detail['message'],
            'Task is not processed yet, please wait'
        )

    def test_data_processed_with_errors_406_NOT_ACCEPTABLE(self):
        csv_task: CSVTask = CSVTaskFactory(error_processing=True, error_message='Why not?')
        with mock.patch.object(
            CSVTask, 'processed', new_callable=mock.PropertyMock
        ) as mock_processed, self.assertRaises(
            api_exceptions.NotAcceptableException
        ) as expected_exception:
            mock_processed.return_value = False
            _ = CSVTaskSerializer(instance=csv_task).data
        self.assertEqual(mock_processed.call_count, 0)
        self.assertEqual(
            expected_exception.exception.detail['message'],
            'Input file for task is not valid'
        )
        self.assertEqual(
            expected_exception.exception.detail['extra']['error'],
            csv_task.error_message
        )

    def test_data_processed_OK(self):
        csv_task: CSVTask = CSVTaskFactory(output_files__total=1)
        expected_data = {
            'uuid': csv_task.uuid.hex,
            'input_file': csv_task.input_file.url,
            'output_files': CSVTaskFileSerializer(csv_task.output_files, many=True).data,
            'initial_input_file_name': csv_task.initial_input_file_name,
        }
        with mock.patch.object(
            CSVTask, 'processed', new_callable=mock.PropertyMock
        ) as mock_processed:
            mock_processed.return_value = True
            self.assertEqual(CSVTaskSerializer(instance=csv_task).data, expected_data)
            self.assertEqual(mock_processed.call_count, 1)
