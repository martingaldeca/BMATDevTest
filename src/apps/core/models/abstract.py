"""
Create here only abstract models that could be used along all the modules of the application.
"""
import logging
import uuid

from django.db import models
from model_utils import models as model_utils_models

logger = logging.getLogger(__name__)


class UUIDModel(models.Model):
    uuid = models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        if name := getattr(self, 'name', None):
            return name
        return f'{self.id}-{self.uuid.hex}'


class TimeStampedUUIDModel(UUIDModel, model_utils_models.TimeStampedModel):
    class Meta:
        abstract = True
