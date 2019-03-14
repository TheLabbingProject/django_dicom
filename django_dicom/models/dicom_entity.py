from django.db import models


class DicomEntityManager(models.Manager):
    UID_FIELD = None
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

    def get_by_uid(self, uid: str):
        if self.UID_FIELD:
            return self.get(**{self.UID_FIELD: uid})
        raise NotImplementedError

    def get_or_create_by_uid(self, uid: str):
        if self.UID_FIELD:
            return self.get_or_create(**{self.UID_FIELD: uid})
        raise NotImplementedError


def possible_header_field(field: models.Field) -> bool:
    validation_dict = DicomEntityManager.NOT_HEADER_FIELD
    valid_type = not isinstance(field, validation_dict["types"])
    valid_name = field.name not in validation_dict["names"]
    return valid_type and valid_name


class DicomEntity(models.Model):
    class Meta:
        abstract = True

    def get_model_header_fields(self) -> list:
        return [
            field for field in self._meta.get_fields() if possible_header_field(field)
        ]

    def update_fields_from_header(self, force: bool = False):
        raise NotImplementedError
