# Generated by Django 2.2.8 on 2020-04-11 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_dicom', '0037_auto_20200409_0655'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('series', 'number')},
        ),
    ]
