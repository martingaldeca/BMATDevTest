import logging

from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from data_processor.models import CSVTask
from data_processor.api.serializers import ProcessFileSerializer, CSVTaskSerializer

logger = logging.getLogger(__name__)


class ProcessFileView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProcessFileSerializer


class CSVTaskView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'
    serializer_class = CSVTaskSerializer
    queryset = CSVTask.objects.all()
