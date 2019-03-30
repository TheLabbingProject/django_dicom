from django.db import models


class DicomEntity(models.Model):
    NOT_HEADER_FIELD = {
        "types": (
            models.OneToOneField,
            models.ForeignKey,
            models.AutoField,
            models.ManyToOneRel,
            models.FileField,
            models.TextField,
        ),
        "names": ("created_at", "b_value"),
    }

    class Meta:
        abstract = True

    def get_model_header_fields(self) -> list:
        return [
            field
            for field in self._meta.get_fields()
            if self.is_possible_header_field(field)
        ]

    def update_fields_from_header(self, force: bool = False):
        raise NotImplementedError

    def is_possible_header_field(self, field: models.Field) -> bool:
        validation_dict = self.NOT_HEADER_FIELD
        valid_type = not isinstance(field, validation_dict["types"])
        valid_name = field.name not in validation_dict["names"]
        return valid_type and valid_name
