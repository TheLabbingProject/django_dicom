SEQUENCE_TYPE_CHOICES = (
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
)
