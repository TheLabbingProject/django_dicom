# Generated by Django 2.2.8 on 2020-03-17 06:24

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_dicom', '0006_auto_20200317_0623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='warnings',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None),
        ),
    ]