def snake_case_to_camel_case(string: str) -> str:
    return "".join([part.title() for part in string.split("_")])

