import os

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_dicom.models import Instance, Series, Patient, Study


@receiver(post_save, sender=Instance)
def post_save_instance_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        try:
            instance.update_fields_from_header()
            existing = Instance.objects.filter(instance_uid=instance.instance_uid)
            if not existing:
                instance.move_file()
                instance.get_or_create_series()
                instance.get_or_create_patient()
                instance.get_or_create_study()
            else:
                os.remove(instance.file.path)
                instance.delete()
        except Exception as e:
            print("failed to update DICOM fields with the following exception:")
            print(e)
            print(e.args)


@receiver(pre_save, sender=Series)
def pre_save_series_model_receiver(sender, instance, *args, **kwargs):
    instance.update_fields_from_header(force=False)
    if not instance.patient:
        instance.patient = instance.instance_set.last().get_or_create_patient()
    if not instance.study:
        instance.study = instance.instance_set.last().get_or_create_study()


@receiver(pre_save, sender=Patient)
def pre_save_patient_model_receiver(sender, instance, *args, **kwargs):
    instance.update_fields_from_header(force=False)


@receiver(pre_save, sender=Study)
def pre_save_study_model_receiver(sender, instance, *args, **kwargs):
    instance.update_fields_from_header(force=False)

