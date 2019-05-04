from django_dicom.models.study import Study
from rest_framework import serializers


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.study.Study` model.
    
    """

    class Meta:
        model = Study
        fields = ("id", "description", "date", "time", "uid")

