import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.helpers import handle_storage
from core.models import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class CSVTaskFile(TimeStampedUUIDModel):
    output_file = models.FileField(
        null=True,
        blank=True,
        upload_to=handle_storage,
        verbose_name=_('Output csv'),
        help_text=_('Csv inputted to be processed.')
    )

    class Meta:
        verbose_name = _('CSV task file')
        verbose_name_plural = _('CSV tasks files')

    def __str__(self):
        return self.output_file.name if self.output_file else 'No file'


class CSVTask(TimeStampedUUIDModel):
    input_file = models.FileField(
        null=True,
        blank=True,
        upload_to=handle_storage,
        verbose_name=_('Input csv'),
        help_text=_('Csv inputted to be processed.'),
    )
    output_files = models.ManyToManyField(
        CSVTaskFile,
        verbose_name=_('Output files'),
        help_text=_("Csv task's output files"),
        through='CSVTaskFileRelation'
    )
    initial_input_file_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        verbose_name=_('Initial input file name'),
        help_text=_(
            'This field is used to compare if a file was previously processed. Can not be 2 CSVTasks with same '
            'initial input file name. We will assume that if ity is the case the file was previusly processed.'
        ),
    )
    error_processing = models.BooleanField(
        default=False,
        verbose_name=_('Error processing'),
        help_text=_('Field that shows if there was any error processing the file')
    )
    error_message = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_('Error message'),
        help_text=_('If the csv process had any error the message will be stored here')
    )

    class Meta:
        verbose_name = _('CSV task')
        verbose_name_plural = _('CSV tasks')

    @property
    def processed(self):
        return bool(self.output_files.count())

    def process(self) -> bool:

        # Each task can be process only once (sanity check)
        if self.processed:
            logger.warning(f'File {str(self)} was processed before')
            return False

        # When the CSVTask process is call the celery task will be started
        from data_processor.tasks.process_csv import task_process_csv
        task_process_csv.delay(self.uuid.hex)
        return True

    @property
    def output_files_urls(self):
        if self.processed:
            return [task_file.output_file.url for task_file in self.output_files.all()]
        return []


class CSVTaskFileRelation(models.Model):
    csv_task = models.ForeignKey(CSVTask, on_delete=models.CASCADE)
    csv_task_file = models.ForeignKey(CSVTaskFile, on_delete=models.CASCADE)
