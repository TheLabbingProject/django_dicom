from django.db import models


class NIfTI(models.Model):
    path = models.CharField(max_length=500, unique=True)
