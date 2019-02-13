import numpy as np
import os
import subprocess

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django_dicom.apps import DjangoDicomConfig
from django_dicom.models.fields import ChoiceArrayField
from django_dicom.models.nifti import NIfTI
from django_dicom.models.patient import Patient
from django_dicom.models.study import Study
from django_dicom.models.validators import digits_and_dots_only


def fix_scanning_sequence_value(value) -> list:
    if type(value) is str:
        return [value]
    else:
        return list(value)


def replace_underscores_with_spaces(value: str):
    return value.replace("_", " ")


class Series(models.Model):
    series_uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Series UID",
    )
    number = models.IntegerField(
        verbose_name="Series Number", validators=[MinValueValidator(0)]
    )
    echo_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    inversion_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )
    repetition_time = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )

    SPIN_ECHO = "SE"
    INVERSION_RECOVERY = "IR"
    GRADIENT_RECALLED = "GR"
    ECHO_PLANAR = "EP"
    RESEARCH_MODE = "RM"
    SCANNING_SEQUENCE_CHOICES = (
        (SPIN_ECHO, "Spin Echo"),
        (INVERSION_RECOVERY, "Inversion Recovery"),
        (ECHO_PLANAR, "Echo Planar"),
        (RESEARCH_MODE, "Research Mode"),
    )
    scanning_sequence = ChoiceArrayField(
        models.CharField(max_length=2, choices=SCANNING_SEQUENCE_CHOICES),
        size=5,
        blank=True,
        null=True,
    )

    SEGMENTED_K_SPACE = "SK"
    MAGNETIZATION_TRANSFER_CONTRAST = "MTC"
    STEADY_STATE = "SS"
    TIME_REVERSED_STEADY_STATE = "TRSS"
    SPOILED = "SP"
    MAG_PREPARED = "MP"
    OVERSAMPLING_PHASE = "OSP"
    NO_SEQUENCE_VARIANT = "NONE"
    SEQUENCE_VARIANT_CHOICES = (
        (SEGMENTED_K_SPACE, "Segmented k-space"),
        (MAGNETIZATION_TRANSFER_CONTRAST, "Magnetization Transfer Contrast"),
        (STEADY_STATE, "Steady State"),
        (TIME_REVERSED_STEADY_STATE, "Time Reversed Steady State"),
        (SPOILED, "Spoiled"),
        (MAG_PREPARED, "MAG Prepared"),
        (OVERSAMPLING_PHASE, "Oversampling Phase"),
        (NO_SEQUENCE_VARIANT, "None"),
    )
    sequence_variant = ChoiceArrayField(
        models.CharField(max_length=4, choices=SEQUENCE_VARIANT_CHOICES),
        blank=True,
        null=True,
    )

    manufacturer = models.CharField(max_length=64, blank=True, null=True)
    manufacturers_model_name = models.CharField(max_length=64, blank=True, null=True)
    magnetic_field_strength = models.FloatField(validators=[MinValueValidator(0)])
    device_serial_number = models.CharField(max_length=64, blank=True, null=True)
    body_part_examined = models.CharField(max_length=16, blank=True, null=True)

    HEAD_FIRST_PRONE = "HFP"
    HEAD_FIRST_SUPINE = "HFS"
    HEAD_FIRST_DECUBITUS_RIGHT = "HFDR"
    HEAD_FIRST_DECUBITUS_LEFT = "HFDL"
    FEET_FIRST_DECUBITUS_RIGHT = "FFDR"
    FEET_FIRST_DECUBITUS_LEFT = "FFDL"
    FEET_FIRST_PRONE = "FFP"
    FEET_FIRST_SUPINE = "FFS"
    LEFT_FIRST_PRONE = "LFP"
    LEFT_FIRST_SUPINE = "LFS"
    RIGHT_FIRST_PRONE = "RFP"
    RIGHT_FIRST_SUPINE = "RFS"
    ANTERIOR_FIRST_DECUBITUS_RIGHT = "AFDR"
    ANTERIOR_FIRST_DECUBITUS_LEFT = "AFDL"
    POSTERIOR_FIRST_DECUBITUS_RIGHT = "PFDR"
    POSTERIOR_FIRST_DECUBITUS_LEFT = "PFDL"
    PATIENT_POSITION_CHOICES = (
        (HEAD_FIRST_PRONE, "Head First-Prone"),
        (HEAD_FIRST_SUPINE, "Head First-Supine"),
        (HEAD_FIRST_DECUBITUS_RIGHT, "Head First-Decubitus Right"),
        (HEAD_FIRST_DECUBITUS_LEFT, "Head First-Decubitus Left"),
        (FEET_FIRST_DECUBITUS_RIGHT, "Feet First-Decubitus Right"),
        (FEET_FIRST_DECUBITUS_LEFT, "Feet First-Decubitus Left"),
        (FEET_FIRST_PRONE, "Feet First-Prone"),
        (FEET_FIRST_SUPINE, "Feet First-Supine"),
        (LEFT_FIRST_PRONE, "Left First-Prone"),
        (LEFT_FIRST_SUPINE, "Left First-Supine"),
        (RIGHT_FIRST_PRONE, "Right First-Prone"),
        (RIGHT_FIRST_SUPINE, "Right First-Supine"),
        (ANTERIOR_FIRST_DECUBITUS_RIGHT, "Anterior First-Decubitus Right"),
        (ANTERIOR_FIRST_DECUBITUS_LEFT, "Anterior First-Decubitus Left"),
        (POSTERIOR_FIRST_DECUBITUS_RIGHT, "Posterior First-Decubitus Right"),
        (POSTERIOR_FIRST_DECUBITUS_LEFT, "Posterior First-Decubitus Left"),
    )
    patient_position = models.CharField(
        max_length=4, choices=PATIENT_POSITION_CHOICES, default=HEAD_FIRST_SUPINE
    )

    MR_ACQUISITION_2D = "2D"
    MR_ACQUISITION_3D = "3D"
    MR_ACQUISITION_TYPE_CHOICES = ((MR_ACQUISITION_2D, "2D"), (MR_ACQUISITION_3D, "3D"))
    mr_acquisition_type = models.CharField(
        max_length=2, choices=MR_ACQUISITION_TYPE_CHOICES, default=MR_ACQUISITION_2D
    )

    AUTOREFRACTION = "AR"
    CONTENT_ASSESSMENT__RESULTS = "ASMT"
    AUDIO = "AU"
    ULTRASOUND_BONE_DENSITOMETRY = "BDUS"
    XRAY_BONE_DENSITOMETRY = "BMD"
    BIOMAGNETIC_IMAGING = "BI"
    COMPUTED_RADIOGRAPHY = "CR"
    COMPUTED_TOMOGRAPHY = "CT"
    COMPUTER_TOMOGRAPHY_PROTOCOL = "CTPROTOCOL"
    DIAPHANOGRAPHY = "DG"
    DOCUMENT = "DOC"
    DIGITAL_RADIOGRAPHY = "DX"
    ELECTROCARDIOGRAPHY = "ECG"
    CARDIAC_ELECTROPHYSIOLOGY = "EPS"
    ENDOSCOPY = "EDS"
    FIDUCIALS = "FID"
    GENERAL_MICROSCOPY = "GM"
    HARD_COPY = "HC"
    HEMODYNAMIC_WAVEFORM = "HD"
    INTRAORAL_RADIOGRAPHY = "IO"
    INTRAOCULAR_LENS_DATA = "IOL"
    INTRAVASCULAR_OPTICAL_COHERENCE_TOMOGRAPHY = "IVOCT"
    INTRAVASCULAR_ULTRASOUND = "IVUS"
    KERATOMETRY = "KER"
    KEY_OBJECT_SELECTION = "KO"
    LENSOMETRY = "LEN"
    LASER_SURFACE_SCAN = "LS"
    MAMMOGRAPHY = "MG"
    MAGNETIC_RESONANCE = "MR"
    MANUFACTURING_3D_MODEL = "M3D"
    NUCLEAR_MEDICINE = "NM"
    OPHTHALMIC_AXIAL_MEASUREMENTS = "OAM"
    OPTICAL_COHERENCE_TOMOGRAPHY = "OCT"
    OPHTHALMIC_PHOTOGRAPHY = "OP"
    OPHTHALMIC_MAPPING = "OPM"
    OPHTHALMIC_TOMOGRAPHY = "OPT"
    OPHTHALMIC_TOMOGRAPHY_B_SCAN_VOLUME_ANALYSIS = "OPTBSV"
    OPHTHALMIC_TOMOGRAPHY_EN_FACE = "OPTENF"
    OPHTHALMIC_VISUAL_FIELD = "OPV"
    OPTICAL_SURFACE_SCAN = "OSS"
    OTHER = "OT"
    PLAN = "PLAN"
    PRESENTATION_STATE = "PR"
    POSITRON_EMISSION_TOMOGRAPHY = "PT"
    PANORAMIC_XRAY = "PX"
    REGISTRATION = "REG"
    RESPIRATORY_WAVEFORM = "RESP"
    RADIO_FLUOROSCOPY = "RF"
    RADIOGRAPHIC_IMAGING = "RG"
    RADIOTHERAPY_DOSE = "RTDOSE"
    RADIOTHERAPY_IMAGE = "RTIMAGE"
    RADIOTHERAPY_PLAN = "RTPLAN"
    RADIOTHERAPY_TREATMENT_RECORD = "RTRECORD"
    RADIOTHERAPY_STRUCTURE_SET = "RESTRUCT"
    REAL_WORLD_VALUE_MAP = "RWV"
    SEGMENTATION = "SEG"
    SLIDE_MICROSCOPY = "SM"
    STEREOMETRIC_RELATIONSHIP = "SMR"
    SR_DOCUMENT = "SR"
    SUBJECTIVE_REFRACTION = "SRF"
    AUTOMATED_SLIDE_STAINER = "STAIN"
    THERMOGRAPHY = "TG"
    ULTRASOUND = "US"
    VISUAL_ACUITY = "VA"
    XRAY_ANGIOGRAPHY = "XA"
    EXTERNAL_CAMERA_PHOTOGRAPHY = "XC"
    MODALITY_CHOICES = (
        (AUTOREFRACTION, "Autorefraction"),
        (CONTENT_ASSESSMENT__RESULTS, "Content Assessment Results"),
        (AUDIO, "Audio"),
        (ULTRASOUND_BONE_DENSITOMETRY, "Bone Densitometry (ultrasound)"),
        (BIOMAGNETIC_IMAGING, "Biomagnetic imaging"),
        (XRAY_BONE_DENSITOMETRY, "Bone Densitometry (X-Ray)"),
        (COMPUTED_RADIOGRAPHY, "Computed Radiography"),
        (COMPUTED_TOMOGRAPHY, "Computed Tomography"),
        (COMPUTER_TOMOGRAPHY_PROTOCOL, "CT Protocol (Performed)"),
        (DIAPHANOGRAPHY, "Diaphanography"),
        (DOCUMENT, "Document"),
        (DIGITAL_RADIOGRAPHY, "Digital Radiography"),
        (ELECTROCARDIOGRAPHY, "Electrocardiography"),
        (CARDIAC_ELECTROPHYSIOLOGY, "Cardiac Electrophysiology"),
        (ENDOSCOPY, "Endoscopy"),
        (FIDUCIALS, "Fiducials"),
        (GENERAL_MICROSCOPY, "General Microscopy"),
        (HARD_COPY, "Hard Copy"),
        (HEMODYNAMIC_WAVEFORM, "Hemodynamic Waveform"),
        (INTRAORAL_RADIOGRAPHY, "Intra-Oral Radiography"),
        (INTRAOCULAR_LENS_DATA, "Intraocular Lens Data"),
        (
            INTRAVASCULAR_OPTICAL_COHERENCE_TOMOGRAPHY,
            "Intravascular Optical Coherence Tomography",
        ),
        (INTRAVASCULAR_ULTRASOUND, "Intravascular Ultrasound"),
        (KERATOMETRY, "Keratometry"),
        (KEY_OBJECT_SELECTION, "Key Object Selection"),
        (LENSOMETRY, "Lensometry"),
        (LASER_SURFACE_SCAN, "Laser surface scan"),
        (MAMMOGRAPHY, "Mammography"),
        (MAGNETIC_RESONANCE, "Magnetic Resonance"),
        (MANUFACTURING_3D_MODEL, "Model for 3D Manufacturing"),
        (NUCLEAR_MEDICINE, "Nuclear Medicine"),
        (OPHTHALMIC_AXIAL_MEASUREMENTS, "Ophthalmic Axial Measurements"),
        (OPTICAL_COHERENCE_TOMOGRAPHY, "Optical Coherence Tomography (non-Ophthalmic)"),
        (OPHTHALMIC_PHOTOGRAPHY, "Ophthalmic Photography"),
        (OPHTHALMIC_MAPPING, "Ophthalmic Mapping"),
        (OPHTHALMIC_TOMOGRAPHY, "Ophthalmic Tomography"),
        (
            OPHTHALMIC_TOMOGRAPHY_B_SCAN_VOLUME_ANALYSIS,
            "Ophthalmic Tomography B-scan Volume Analysis",
        ),
        (OPHTHALMIC_TOMOGRAPHY_EN_FACE, "Ophthalmic Tomography En Face"),
        (OPHTHALMIC_VISUAL_FIELD, "Ophthalmic Visual Field"),
        (OPTICAL_SURFACE_SCAN, "Optical Surface Scan"),
        (OTHER, "Other"),
        (PLAN, "Plan"),
        (PRESENTATION_STATE, "Presentation State"),
        (POSITRON_EMISSION_TOMOGRAPHY, "Positron emission tomography (PET)"),
        (PANORAMIC_XRAY, "Panoramic X-Ray"),
        (REGISTRATION, "Registration"),
        (RESPIRATORY_WAVEFORM, "Respiratory Waveform"),
        (RADIO_FLUOROSCOPY, "Radio Fluoroscopy"),
        (RADIOGRAPHIC_IMAGING, "Radiographic imaging (conventional film/screen)"),
        (RADIOTHERAPY_DOSE, "Radiotherapy Dose"),
        (RADIOTHERAPY_IMAGE, "Radiotherapy Image"),
        (RADIOTHERAPY_PLAN, "Radiotherapy Plan"),
        (RADIOTHERAPY_TREATMENT_RECORD, "RT Treatment Record"),
        (RADIOTHERAPY_STRUCTURE_SET, "Radiotherapy Structure Set"),
        (REAL_WORLD_VALUE_MAP, "Real World Value Map"),
        (SEGMENTATION, "Segmentation"),
        (SLIDE_MICROSCOPY, "Slide Microscopy"),
        (STEREOMETRIC_RELATIONSHIP, "Stereometric Relationship"),
        (SR_DOCUMENT, "SR Document"),
        (SUBJECTIVE_REFRACTION, "Subjective Refraction"),
        (AUTOMATED_SLIDE_STAINER, "Automated Slide Stainer"),
        (THERMOGRAPHY, "Thermography"),
        (ULTRASOUND, "Ultrasound"),
        (VISUAL_ACUITY, "Visual Acuity"),
        (XRAY_ANGIOGRAPHY, "X-Ray Angiography"),
        (EXTERNAL_CAMERA_PHOTOGRAPHY, "External-camera Photography"),
    )
    modality = models.CharField(
        max_length=10, choices=MODALITY_CHOICES, default=MAGNETIC_RESONANCE
    )

    date = models.DateField()
    time = models.TimeField()
    description = models.CharField(max_length=64)
    nifti = models.OneToOneField(
        "django_dicom.nifti", on_delete=models.CASCADE, blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    study = models.ForeignKey(
        Study, blank=True, null=True, on_delete=models.PROTECT, related_name="series"
    )
    patient = models.ForeignKey(
        Patient, blank=True, null=True, on_delete=models.PROTECT, related_name="series"
    )

    ATTRIBUTE_FORMATTING = {
        "InstanceNumber": int,
        "InversionTime": float,
        "EchoTime": float,
        "RepetitionTime": float,
        "PixelBandwidth": float,
        "SAR": float,
        "FlipAngle": float,
        "ScanningSequence": fix_scanning_sequence_value,
        "Manufacturer": str.capitalize,
        "ManufacturersModelName": str.capitalize,
        "MagneticFieldStrength": float,
        "InstitutionName": replace_underscores_with_spaces,
        "BodyPartExamined": str.capitalize,
    }

    def __str__(self):
        return self.series_uid

    def get_absolute_url(self):
        return reverse("dicom:series_detail", args=[str(self.id)])

    def get_data(self) -> np.ndarray:
        instances = self.instance_set.order_by("number")
        return np.stack(
            [instance.read_data().pixel_array for instance in instances], axis=-1
        )

    def to_dict(self):
        return {
            "id": f"series_{self.id}",
            "icon": "fas fa-flushed",
            "text": self.description,
        }

    def get_path(self):
        return os.path.dirname(self.instance_set.first().file.path)

    def get_default_nifti_dir(self):
        return os.path.join(os.path.dirname(self.get_path()), "NIfTI")

    def to_nifti(self, dest: str = None):
        if not self.nifti:
            dcm2nii = getattr(DjangoDicomConfig, "dcm2niix_path")
            if dcm2nii:
                if not dest:
                    dest = self.get_default_nifti_dir()
                    os.makedirs(dest, exist_ok=True)
                command = [
                    dcm2nii,
                    "-z",
                    "y",
                    "-b",
                    "n",
                    "-o",
                    dest,
                    "-f",
                    f"{self.id}",
                    self.get_path(),
                ]
                subprocess.check_output(command)
                path = os.path.join(dest, f"{self.id}.nii.gz")
                nifti_instance = NIfTI(path=path)
                nifti_instance.save()
                self.nifti = nifti_instance
                self.save()
            else:
                raise NotImplementedError(
                    "Could not call dcm2niix! Please check settings configuration."
                )
        else:
            return self.nifti

    def show(self):
        mricrogl_path = getattr(DjangoDicomConfig, "mricrogl_path")

        if self.nifti is None:
            self.to_nifti()
        with open(
            "/home/flavus/Projects/django_dicom/django_dicom/template.gls", "r"
        ) as template_file:
            template = template_file.read()

        edited = template.replace("FILE_PATH", self.nifti.path)
        with open("tmp.gls", "w") as script:
            script.write(edited)
        try:
            subprocess.check_call([mricrogl_path, "tmp.gls"])
        except subprocess.CalledProcessError:
            pass
        os.remove("tmp.gls")

    def get_instances_values(self, field_name) -> list:
        return [
            instance.headers.get(field_name)
            for instance in self.instances.order_by("number").all()
        ]

    def get_distinct_values(self, field_name: str) -> list:
        values = self.get_instances_values(field_name)
        if any(values):
            try:
                return list(set(values))
            except TypeError:
                unique = []
                for value in values:
                    if value not in unique:
                        unique += [value]
                return unique
        return None

    def get_series_attribute(self, field_name: str):
        distinct = self.get_distinct_values(field_name)
        if distinct is not None and len(distinct) == 1:
            try:
                return self.ATTRIBUTE_FORMATTING[field_name](distinct.pop())
            except (TypeError, KeyError):
                return distinct.pop()
        elif distinct is not None and len(distinct) > 1:
            values = self.get_instances_values(field_name)
            try:
                return [
                    self.ATTRIBUTE_FORMATTING[field_name](value) for value in values
                ]
            except (TypeError, KeyError):
                return values
        return None

    def get_scanning_sequence_display(self) -> list:
        return [
            [
                sequence_name
                for sequence_code, sequence_name in self.SCANNING_SEQUENCE_CHOICES
                if sequence_code == sequence_type
            ][0]
            for sequence_type in self.scanning_sequence
        ]

    def get_gradient_directions(self):
        return list(
            zip(
                *[
                    instance.gradient_direction
                    for instance in self.instances.order_by("number").all()
                ]
            )
        )

    class Meta:
        verbose_name_plural = "Series"
