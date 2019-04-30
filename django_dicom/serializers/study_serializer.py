from django_dicom.models.study import Study
from rest_framework import serializers


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """
    A serializer_ class for the :class:`~django_dicom.models.study.Study` model.

    .. serializer: https://www.django-rest-framework.org/api-guide/serializers/
    
    """

    class Meta:
        model = Study
        fields = ("id", "description", "date", "time", "uid")

