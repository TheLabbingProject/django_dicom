import os

from datetime import datetime

TEST_FILES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
TEST_ZIP_PATH = os.path.join(TEST_FILES_PATH, "001.zip")
TEST_IMAGE_PATH = os.path.join(TEST_FILES_PATH, "001.dcm")
TEST_DWI_IMAGE_PATH = os.path.join(TEST_FILES_PATH, "dwi_image.dcm")
TEST_DIFFERENT_PATIENT_IMAGE_PATH = os.path.join(
    TEST_FILES_PATH, "different_patient.dcm"
)
TEST_DIFFERENT_STUDY_IMAGE_PATH = os.path.join(TEST_FILES_PATH, "different_study.dcm")

TEST_IMAGE_FIELDS = {
    "dcm": TEST_IMAGE_PATH,
    "uid": "1.3.12.2.1107.5.2.43.66024.2018050112252318571884482",
    "number": 1,
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:25:23.268000", "%H:%M:%S.%f").time(),
}
TEST_DWI_IMAGE_FIELDS = {
    "dcm": TEST_DWI_IMAGE_PATH,
    "uid": "1.3.12.2.1107.5.2.43.66024.2018050112561270026140163",
    "number": 1,
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:56:58.328000", "%H:%M:%S.%f").time(),
}
TEST_SERIES_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.2018050112250992296484473.0.0.0",
    "number": 1,
    "description": "localizer_3D_2 (9X5X5)",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:25:23.265000", "%H:%M:%S.%f").time(),
    "echo_time": 3.04,
    "repetition_time": 7.6,
    "inversion_time": None,
    "scanning_sequence": ["GR"],
    "sequence_variant": ["SP", "OSP"],
    "pixel_spacing": [0.48828125, 0.48828125],
    "manufacturer": "SIEMENS",
    "manufacturer_model_name": "Prisma",
    "magnetic_field_strength": 3.0,
    "device_serial_number": "66024",
    "body_part_examined": "BRAIN",
    "patient_position": "HFS",
    "modality": "MR",
    "institution_name": "Tel-Aviv University",
    "protocol_name": "localizer_3D_2 (9X5X5)",
    "flip_angle": 20.0,
    "mr_acquisition_type": "2D",
    "slice_thickness": 6.0,
    "echo_train_length": 1,
    "operators_name": "Irina",
}
TEST_DWI_SERIES_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.2018050112551393877039165.0.0.0",
    "number": 13,
    "description": "AxCaliber3D1_ep2d_advdiff_30dir_b3000_d11.3D60",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:56:58.324000", "%H:%M:%S.%f").time(),
    "echo_time": 94.0,
    "repetition_time": 3300.0,
    "inversion_time": None,
    "scanning_sequence": ["EP"],
    "sequence_variant": ["SK", "SP"],
    "pixel_spacing": [2.2045454978943, 2.2045454978943],
    "manufacturer": "SIEMENS",
    "manufacturer_model_name": "Prisma",
    "magnetic_field_strength": 3.0,
    "device_serial_number": "66024",
    "body_part_examined": "BRAIN",
    "patient_position": "HFS",
    "modality": "MR",
    "institution_name": "Tel-Aviv University",
    "protocol_name": "AxCaliber3D1_ep2d_advdiff_30dir_b3000_d11.3D60",
    "flip_angle": 180.0,
    "mr_acquisition_type": "2D",
    "slice_thickness": 2.2000000476837,
    "echo_train_length": 32,
    "operators_name": "Irina",
}


TEST_STUDY_FIELDS = {
    "uid": "1.3.12.2.1107.5.2.43.66024.30000018050107081466900000007",
    "description": "YA_lab^Assi",
    "date": datetime.strptime("20180501", "%Y%m%d").date(),
    "time": datetime.strptime("12:21:56.958000", "%H:%M:%S.%f").time(),
}
TEST_PATIENT_FIELDS = {
    "uid": "304848286",
    "date_of_birth": datetime.strptime("19901214", "%Y%m%d").date(),
    "sex": "M",
    "given_name": "Zvi",
    "family_name": "Baratz",
}

