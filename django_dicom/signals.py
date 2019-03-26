from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_dicom.models import Instance, Patient, Series, Study


@receiver(pre_save, sender=Instance)
def pre_save_instance_model_receiver(sender, instance, *args, **kwargs):
    instance.update_fields_from_header(force=True)
    try:
        _ = Instance.objects.get_by_uid(instance.instance_uid)
        raise IntegrityError("Existing instance found!")
    except ObjectDoesNotExist:
        instance.series, _ = instance.get_or_create_by_uid(Series)
        instance.move_file()


@receiver(post_save, sender=Instance)
def post_save_instance_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.series.save()


@receiver(pre_save, sender=Series)
def pre_save_series_model_receiver(sender, instance, *args, **kwargs):
    if not instance.is_updated and instance.has_instances:
        instance.update_fields_from_header(force=False)
        first_instance = instance.instance_set.first()
        instance.patient, _ = first_instance.get_or_create_by_uid(Patient)
        instance.study, _ = first_instance.get_or_create_by_uid(Study)


@receiver(post_save, sender=Series)
def post_save_series_model_receiver(sender, instance, created, *args, **kwargs):
    if instance.patient:
        instance.patient.save()
    if instance.study:
        instance.study.save()


@receiver(pre_save, sender=Patient)
@receiver(pre_save, sender=Study)
def pre_save_model_receiver(sender, instance, *args, **kwargs):
    if not instance.is_updated and instance.has_series:
        instance.update_fields_from_header(force=False)


# This current set-up means that any changes made to header originated fields
# are meaningless - once the save() method is called the pre_save hook will
# forcefully re-read the header data. If changes are made to a related model's
# header field, these will also not be reflected because of the soft update for
# related models.
# Generally speaking - DicomEntities should not be updated! Instead, remove and
# recreate the desired instances.
