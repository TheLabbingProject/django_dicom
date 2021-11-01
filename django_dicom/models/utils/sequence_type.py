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
    ("Diffusion", (("dwi", "DWI"), ("dwi_fieldmap", "DWI Fieldmap"))),
    (
        "Functional",
        (
            ("bold", "fMRI"),
            ("func_fieldmap", "fMRI Fieldmap"),
            ("func_sbref", "fMRI SBRef"),
        ),
    ),
    ("", "Unknown"),
)
