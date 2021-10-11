"""
Messages for the :mod:`django_dicom.views` module.
"""
from django_dicom.utils.configuration import COUNT_FILTERING_KEY

COUNT_FILTERING_DISABLED: str = f"{COUNT_FILTERING_KEY} is set to false, to query aggregated values please change this settings to true."


# flake8: noqa: E501
