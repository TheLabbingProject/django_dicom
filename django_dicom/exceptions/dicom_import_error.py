"""
Definition of the
:class:`~django_dicom.excepetions.dicom_import_error.DicomImportError`
class.
"""


class DicomImportError(Exception):
    """
    Raised whenever importing new DICOM data to the database fails.
    """

    pass
