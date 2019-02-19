from django_dicom.models.choice_enum import ChoiceEnum


class PatientPosition(ChoiceEnum):
    HFP = "Head First-Prone"
    HFS = "Head First-Supine"
    HFDR = "Head First-Decubitus Right"
    HFDL = "Head First-Decubitus Left"
    FFDR = "Feet First-Decubitus Right"
    FFDL = "Feet First-Decubitus Left"
    FFP = "Feet First-Prone"
    FFS = "Feet First-Supine"
    LFP = "Left First-Prone"
    LFS = "Left First-Supine"
    RFP = "Right First-Prone"
    RFS = "Right First-Supine"
    AFDR = "Anterior First-Decubitus Right"
    AFDL = "Anterior First-Decubitus Left"
    PFDR = "Posterior First-Decubitus Right"
    PFDL = "Posterior First-Decubitus Left"