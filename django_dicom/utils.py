def snake_case_to_camel_case(string: str) -> str:
    return "".join([part.title() for part in string.split("_")])


SCANNING_SEQUENCE = {
    "mprage": {"GR", "IR"},
    "spgr": {"GR"},
    "fspgr": {"GR"},
    "flair": {"SE", "IR"},
    "dti": [{"EP", "SE"}, {"EP", "RM"}],
    "fmri": [{"EP"}, {"EP", "GR"}],
    "localizer": {"GR"},
    "ir-epi": {"EP", "IR"},
    "ep2d": {"EP"},
    "fse": {"SE"},
}

SEQUENCE_VARIANT = {
    "mprage": {"SK", "SP", "MP"},
    "spgr": {"SK", "SP", "SS"},
    "fspgr": {"SK", "SS"},
    "flair": {"SK", "SP", "MP"},
    "dti": {"NONE"},
    "fmri": [{"SK", "SS"}, {"SS"}],
    "localizer": {"SP", "OSP"},
    "ir-epi": {"SK", "SP", "MP", "OSP"},
    "ep2d": {"SK", "SP"},
    "fse": {"SK"},
}


def check_scanning_sequence(scan_instance, string_id: str) -> bool:
    expected_scanning_sequence = SCANNING_SEQUENCE.get(string_id, set())
    if isinstance(expected_scanning_sequence, set):
        return set(scan_instance.scanning_sequence) == expected_scanning_sequence
    elif isinstance(expected_scanning_sequence, (list, tuple)):
        return set(scan_instance.scanning_sequence) in expected_scanning_sequence
    return False


def check_sequence_variant(scan_instance, string_id: str) -> bool:
    expected_sequence_variant = SEQUENCE_VARIANT.get(string_id, set())
    if isinstance(expected_sequence_variant, set):
        return set(scan_instance.sequence_variant) == expected_sequence_variant
    elif isinstance(expected_sequence_variant, (list, tuple)):
        return set(scan_instance.sequence_variant) in expected_sequence_variant
    return False


def check_sequence_type(scan_instance, string_id: str) -> bool:
    try:
        matching_scanning_sequence = check_scanning_sequence(scan_instance, string_id)
        matching_sequence_variant = check_sequence_variant(scan_instance, string_id)
    except TypeError:
        return False
    return matching_scanning_sequence and matching_sequence_variant
