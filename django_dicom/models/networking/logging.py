import logging

from django_dicom.models.networking import messages

logger = logging.getLogger("data.dicom.networking")


def log_c_store_received(level=logging.DEBUG) -> None:
    message = messages.C_STORE_RECEIVED
    logger.log(level, message)


def log_dataset_saved(file_name: str, level=logging.DEBUG) -> None:
    message = messages.WRITE_DICOM_END.format(file_name=file_name)
    logger.log(level, message)


def log_import_start(file_name: str, level=logging.DEBUG) -> None:
    message = messages.IMAGE_IMPORT_START.format(file_name=file_name)
    logger.log(level, message)


def log_import_end(file_name: str, level=logging.DEBUG) -> None:
    message = messages.IMAGE_IMPORT_END.format(file_name=file_name)
    logger.log(level, message)


def log_cleanup_start(file_name: str, level=logging.DEBUG) -> None:
    message = messages.TEMP_DICOM_REMOVAL_START.format(file_name=file_name)
    logger.log(level, message)


def log_cleanup_end(file_name: str, level=logging.DEBUG) -> None:
    message = messages.TEMP_DICOM_REMOVAL_END.format(file_name=file_name)
    logger.log(level, message)
