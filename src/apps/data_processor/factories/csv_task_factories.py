import random

import factory.django
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from data_processor.models import CSVTaskFile, CSVTask, CSVTaskFileRelation


class CSVTaskFileFactory(DjangoModelFactory):
    class Meta:
        model = CSVTaskFile

    output_file = factory.django.FileField(filename='test.csv')


class CSVTaskFactory(DjangoModelFactory):
    class Meta:
        model = CSVTask

    input_file = factory.django.FileField()
    initial_input_file_name = FuzzyText()
    error_processing = False
    error_message = None

    @factory.post_generation
    def output_files(self: CSVTask, create, extracted, **kwargs):
        _min = kwargs.get('min', 1)
        _max = kwargs.get('max', 3)
        if _total := kwargs.get('total', None):
            _min = _max = _total

        if _min > _max:
            raise ValueError('min value lower than max in factory')
        if _total != 0:
            for i in range(random.randint(_min, _max)):
                CSVTaskFileRelationFactory(csv_task=self, csv_task_file=CSVTaskFileFactory())


class CSVTaskFileRelationFactory(DjangoModelFactory):
    class Meta:
        model = CSVTaskFileRelation

    csv_task = factory.SubFactory(CSVTaskFactory)
    csv_task_file = factory.SubFactory(CSVTaskFileFactory)
