# Generated by Django 2.1.5 on 2019-02-12 14:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_dicom', '0011_auto_20190212_1355'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instance',
            name='slice_timing',
        ),
    ]
