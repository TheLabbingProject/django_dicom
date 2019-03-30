import numpy as np
import pandas as pd

from django_dicom.models import Patient


def between_subjects(bins: int = 10) -> pd.DataFrame:
    patient_ids = list(Patient.objects.values_list("patient_id", flat=True))
    results = pd.DataFrame(index=patient_ids, columns=patient_ids)
    for reference in Patient.objects.all():
        for other in Patient.objects.all():
            if results.loc[reference.patient_id, other.patient_id] is np.nan:
                mutual_information_score = reference.calculate_mutual_information(
                    other, bins
                )
                results.loc[
                    reference.patient_id, other.patient_id
                ] = mutual_information_score
                results.loc[
                    other.patient_id, reference.patient_id
                ] = mutual_information_score
    return results


def within_subject(bins: int = 10) -> pd.Series:
    results = pd.Series()
    for patient in Patient.objects.all():
        reference = patient.get_second_session_anatomical()
        if reference:
            default = patient.get_default_anatomical()
            results[patient.patient_id] = default.calculate_mutual_information(
                reference
            )
    return results
