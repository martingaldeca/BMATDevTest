from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from core.exceptions import api as api_exceptions
from data_processor.models import CSVTaskFile, CSVTask


class ProcessFileSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)
    file = serializers.FileField(
        write_only=True,
        source='input_file',
        validators=[
            FileExtensionValidator(
                allowed_extensions=["csv"]
            )
        ]
    )

    class Meta:
        model = CSVTask
        fields = ['uuid', 'file']

    def validate_file(self, value):
        query = CSVTask.objects.filter(initial_input_file_name=value.name)
        if query.exists():
            csv_task = query.last()
            raise api_exceptions.ConflictException(
                message=f'The file was previously processed in task {csv_task.uuid.hex}',
                uuid=csv_task.uuid.hex
            )
        self.context['initial_input_file_name'] = value.name
        return value

    def save(self, **kwargs):
        csv_task: CSVTask = super(ProcessFileSerializer, self).save(**kwargs)
        csv_task.initial_input_file_name = self.context['initial_input_file_name']
        csv_task.save()
        if csv_task.process():
            return csv_task
        else:
            # Sanity check it should never happen in the API
            raise api_exceptions.PreconditionFailedException(
                message=f'The file was previously processed in task {csv_task.uuid.hex}',
                uuid=csv_task.uuid.hex
            )


class CSVTaskFileSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:
        model = CSVTaskFile
        fields = ['uuid', 'output_file']


class CSVTaskSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(format='hex')
    output_files = CSVTaskFileSerializer(many=True, read_only=True)

    class Meta:
        model = CSVTask
        fields = ['uuid', 'input_file', 'output_files', 'initial_input_file_name']
        read_only_fields = ['input_file', 'output_files', 'initial_input_file_name']

    @property
    def data(self):
        csv_task: CSVTask = self.instance
        if csv_task.error_processing:
            raise api_exceptions.NotAcceptableException(
                message='Input file for task is not valid',
                extra={
                    'error': csv_task.error_message
                },
            )
        if csv_task.processed:
            return super(CSVTaskSerializer, self).data
        else:
            raise api_exceptions.TooEarlyException(message='Task is not processed yet, please wait')
