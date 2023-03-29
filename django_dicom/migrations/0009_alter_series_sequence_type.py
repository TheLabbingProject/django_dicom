# Generated by Django 3.2.6 on 2021-11-23 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("django_dicom", "0008_alter_series_sequence_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="series",
            name="sequence_type",
            field=models.CharField(
                blank=True,
                choices=[
                    (
                        "Anatomical",
                        (
                            ("localizer", "Localizer"),
                            ("flair", "FLAIR"),
                            ("ir_epi", "IR-EPI"),
                            ("mprage", "MPRAGE"),
                            ("t2w", "T2-weighted"),
                        ),
                    ),
                    (
                        "Diffusion",
                        (
                            ("dwi", "DWI"),
                            ("dwi_sbref", "DWI SBRef"),
                            ("dwi_derived", "DWI (derived)"),
                        ),
                    ),
                    (
                        "Functional",
                        (
                            ("bold", "fMRI"),
                            ("func_fieldmap", "fMRI Fieldmap"),
                            ("func_sbref", "fMRI SBRef"),
                        ),
                    ),
                    ("Physiological", (("physio_log", "Physio Log"),)),
                    ("", "Unknown"),
                ],
                max_length=64,
                null=True,
            ),
        ),
    ]