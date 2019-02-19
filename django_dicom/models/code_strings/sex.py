from django_dicom.models.choice_enum import ChoiceEnum


class Sex(ChoiceEnum):
    M = "Male"
    F = "Female"
    O = "Other"
