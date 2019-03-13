from django.db import models


class DicomEntity(models.Model):
    class Meta:
        abstract = True

    NOT_HEADER_FIELD = {
        "types": (
            models.OneToOneField,
            models.ForeignKey,
            models.AutoField,
            models.ManyToOneRel,
            models.FileField,
        ),
        "names": ("created_at", "b_value"),
    }

    def possible_header_field(self, field: models.Field) -> bool:
        valid_type = not isinstance(field, self.NOT_HEADER_FIELD["types"])
        valid_name = field.name not in self.NOT_HEADER_FIELD["names"]
        return valid_type and valid_name

    def get_model_header_fields(self) -> list:
        return [
            field
            for field in self._meta.get_fields()
            if self.possible_header_field(field)
        ]

    def update_fields_from_header(self, force=False):
        raise NotImplementedError
