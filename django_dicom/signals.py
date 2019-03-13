import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django_dicom.models import Instance


@receiver(post_save, sender=Instance)
def post_save_instance_model_receiver(sender, instance, created, *args, **kwargs):
    if created:
        print("Creating new instance...")
        try:
            print("Updating fields...", end="\t")
            instance.update_fields_from_header()
            print("done!")
            existing = Instance.objects.filter(instance_uid=instance.instance_uid)
            if not existing:
                print("Moving file...", end="\t")
                instance.move_file()
                print("done!")
                instance.save()
                print("Updating parents...", end="\t")
                instance.get_or_create_series()
                instance.get_or_create_patient()
                instance.get_or_create_study()
                print("done!")
            else:
                print(f"Found existing instance with UID={instance.instance_uid}!!!")
                os.remove(instance.file.path)
                instance.delete()
        except Exception as e:
            print("failed to update DICOM fields with the following exception:")
            print(e)
