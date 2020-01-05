from django_dicom.models.study import Study
from rest_framework import serializers


class StudySerializer(serializers.HyperlinkedModelSerializer):
    """
    A `serializer <https://www.django-rest-framework.org/api-guide/serializers/>`_ class for the :class:`~django_dicom.models.study.Study` model.
    
    """

    url = serializers.HyperlinkedIdentityField(view_name="dicom:study-detail")

    class Meta:
        model = Study
        fields = "id", "url", "description", "date", "time", "uid"

