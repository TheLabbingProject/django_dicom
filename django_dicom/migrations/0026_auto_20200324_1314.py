# Generated by Django 2.2.8 on 2020-03-24 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_dicom', '0025_auto_20200321_1213'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='header',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='image', to='django_dicom.Header'),
        ),
    ]