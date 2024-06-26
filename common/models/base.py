import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from common.manager import BaseObjectManagerQuerySet

COMMON_CHAR_FIELD_MAX_LENGTH = 512
COMMON_NULLABLE_FIELD_CONFIG = {
    "default": None,
    "null": True,
}
COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG = {
    **COMMON_NULLABLE_FIELD_CONFIG,
    "blank": True,
}


class BaseModel(models.Model):
    """Base Model for this Application"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = BaseObjectManagerQuerySet.as_manager()
    DoesNotExist: ObjectDoesNotExist

    class Meta:
        abstract = True
