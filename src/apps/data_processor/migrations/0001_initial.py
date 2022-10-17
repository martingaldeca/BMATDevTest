# Generated by Django 4.0.8 on 2022-10-17 00:04

import core.helpers.storage_helpers
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CSVTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('input_file', models.FileField(blank=True, help_text='Csv inputted to be processed.', null=True, upload_to=core.helpers.storage_helpers.handle_storage, verbose_name='Input csv')),
                ('initial_input_file_name', models.CharField(blank=True, db_index=True, help_text='This field is used to compare if a file was previously processed. Can not be 2 CSVTasks with same initial input file name. We will assume that if ity is the case the file was previusly processed.', max_length=128, null=True, unique=True, verbose_name='Initial input file name')),
                ('error_processing', models.BooleanField(default=False, help_text='Field that shows if there was any error processing the file', verbose_name='Error processing')),
                ('error_message', models.CharField(blank=True, help_text='If the csv process had any error the message will be stored here', max_length=128, null=True, verbose_name='Error message')),
            ],
            options={
                'verbose_name': 'CSV task',
                'verbose_name_plural': 'CSV tasks',
            },
        ),
        migrations.CreateModel(
            name='CSVTaskFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('output_file', models.FileField(blank=True, help_text='Csv inputted to be processed.', null=True, upload_to=core.helpers.storage_helpers.handle_storage, verbose_name='Output csv')),
            ],
            options={
                'verbose_name': 'CSV task file',
                'verbose_name_plural': 'CSV tasks files',
            },
        ),
        migrations.CreateModel(
            name='CSVTaskFileRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_processor.csvtask')),
                ('csv_task_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_processor.csvtaskfile')),
            ],
        ),
        migrations.AddField(
            model_name='csvtask',
            name='output_files',
            field=models.ManyToManyField(help_text="Csv task's output files", through='data_processor.CSVTaskFileRelation', to='data_processor.csvtaskfile', verbose_name='Output files'),
        ),
    ]