import json
import numpy as np
import pydicom

from django.db import models
from django.urls import reverse
from django_dicom.models.dicom_entity import DicomEntity
from django_dicom.models.validators import digits_and_dots_only, validate_file_extension
from django_dicom.reader import HeaderInformation
from django_dicom.utils import NumpyEncoder


class Image(DicomEntity):
    """
    A model to represent a single DICOM_ image. This model is meant to be
    instantiated with the `file` field set to some *.dcm* file, and then it is
    updated automatically by inspection of the file's header information.

    .. _DICOM: https://www.dicomstandard.org/
    
    """

    # Stores a reference to the image file.
    dcm = models.FileField(
        max_length=250, upload_to="dicom", validators=[validate_file_extension]
    )

    uid = models.CharField(
        max_length=64,
        unique=True,
        validators=[digits_and_dots_only],
        verbose_name="Image UID",
    )
    number = models.IntegerField(verbose_name="Image Number")
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)

    series = models.ForeignKey("django_dicom.Series", on_delete=models.PROTECT)

    _header = None
    FIELD_TO_HEADER = {
        "uid": "SOPInstanceUID",
        "number": "InstanceNumber",
        "date": "InstanceCreationDate",
        "time": "InstanceCreationTime",
    }

    class Meta:
        indexes = [models.Index(fields=["uid"]), models.Index(fields=["date", "time"])]

    def __str__(self) -> str:
        return self.uid

    def get_absolute_url(self) -> str:
        return reverse("dicom:image_detail", args=[str(self.id)])

    def read_file(self, header_only: bool = False) -> pydicom.FileDataset:
        """
        Reads the DICOM image file to memory.
        
        Parameters
        ----------
        header_only : bool, optional
            Exclude pixel data or not, by default False which will include pixel data.
        
        Returns
        -------
        :class:`pydicom.dataset.FileDataset`
            DICOM image file as object.
        """
        return pydicom.read_file(self.dcm.path, stop_before_pixels=header_only)

    def get_data(self, as_json: bool = False) -> np.ndarray:
        """
        Returns the image's pixel array as a `NumPy`_ array or as a JSON-like string if *as_json* is True.
        
        .. _NumPy: http://www.numpy.org/

        Parameters
        ----------
        as_json : bool
            Return the pixel array as a JSON formatted string.

        Returns
        -------
        :class:`numpy.ndarray`
            Image's pixel array.
        """

        data = self.read_file(header_only=False).pixel_array
        if as_json:
            return json.dumps({"data": data}, cls=NumpyEncoder)
        return data

    def read_header(self) -> HeaderInformation:
        """
        Reads the header information from the associated DICOM file.
        
        Returns
        -------
        :class:`~django_dicom.reader.header_information.HeaderInformation`
            Image's header information.
        """

        raw_header = self.read_file(header_only=True)
        return HeaderInformation(raw_header)

    def get_b_value(self) -> int:
        """
        Returns the `b-value`_ for diffusion weighted images (`DWI`_). 
        Currently only SIEMENS tags are supported.

        .. _b-value: https://radiopaedia.org/articles/b-values-1
        .. _DWI: https://en.wikipedia.org/wiki/Diffusion_MRI#Diffusion_imaging

        Returns
        -------
        int
            Degree of diffusion weighting applied.
        """

        manufacturer = self.header.get_value("Manufacturer")
        if manufacturer == "SIEMENS":
            return self.header.get_value(("0019", "100c"))

    @property
    def header(self) -> HeaderInformation:
        """
        Caches the created :class:`~django_dicom.reader.header_information.HeaderInformation`
        instance to prevent multiple reades.
        
        Returns
        -------
        :class:`~django_dicom.reader.header_information.HeaderInformation`
            The image's header information.
        """

        if not isinstance(self._header, HeaderInformation):
            self._header = self.read_header()
        return self._header

    @property
    def slice_timing(self) -> list:
        """
        Returns the slice timing vector for this image. 
        Currently only SIEMENS tags are supported.
        
        Returns
        -------
        list
            This image's slice times.
        """
        manufacturer = self.header.get_value("Manufacturer")
        if manufacturer == "SIEMENS":
            return self.header.get_value(("0019", "1029"))

    @property
    def gradient_direction(self) -> list:
        """
        Returns the gradient direction vector for this image. 
        Currently only SIEMENS tags are supported.
        
        Returns
        -------
        list
            This image's gradient direction.
        """
        manufacturer = self.header.get_value("Manufacturer")
        if manufacturer == "SIEMENS":
            return self.header.get_value(("0019", "100e"))

