import os
from django.db import models


class NIfTI(models.Model):
    path = models.CharField(max_length=500, unique=True)

    @property
    def b_value(self) -> list:
        file_name = self.path.replace('nii.gz', 'bval')
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file_object:
                content = file_object.read()
            content = content.splitlines()[0].split('\t')
            return [int(value) for value in content]
        return None

    @property
    def b_vector(self) -> list:
        file_name = self.path.replace('nii.gz', 'bvec')
        if os.path.isfile(file_name):
            with open(file_name, 'r') as file_object:
                content = file_object.read()
            return [[float(value) for value in vector.rstrip().split('\t')]
                    for vector in content.rstrip().split('\n')]
        return None
