# Generated by Django 2.2.8 on 2020-04-03 04:40

from django.db import migrations, models
import django_dicom.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ('django_dicom', '0034_remove_dataelementdefinition_value_multiplicity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dataelement',
            options={'ordering': ('header', 'definition')},
        ),
        migrations.AlterField(
            model_name='image',
            name='dcm',
            field=models.FileField(max_length=1000, upload_to='dicom', validators=[django_dicom.models.validators.validate_file_extension], verbose_name='File Path'),
        ),
    ]
