from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django_dicom.models import Instance


@receiver(pre_save, sender=Instance)
def pre_save_instance_model_receiver(sender, instance, *args, **kwargs):
    instance.update_fields_from_header(force=True)


@receiver(post_save, sender=Instance)
def post_save_instance_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.move_file()
        instance.create_relations()
        instance.create_series_relations(force=False)
        instance.save()
    else:
        instance.update_related_from_headers(force=False)


# This current set-up means that any changes made to header originated fields
# are meaningless - once the save() method is called the pre_save hook will
# forcefully re-read the header data. If changes are made to a related model's
# header field, these will also not be reflected because of the soft update for
# related models.
# Generally speaking - DicomEntities should not be updated! Instead, remove and
# recreate the desired instances.
