from django.contrib.auth.models import AbstractUser
from django.db import models

from access.config import GenderChoices, UserTypeChoices
from access.manager import AppUserManagerQuerySet
from common.models import (
    COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG,
    COMMON_CHAR_FIELD_MAX_LENGTH,
    BaseModel,
)


class User(BaseModel, AbstractUser):
    """Base User Model"""

    objects = AppUserManagerQuerySet.as_manager()

    email = models.EmailField(blank=False, unique=True)
    type = models.CharField(
        choices=UserTypeChoices.choices,
        max_length=COMMON_CHAR_FIELD_MAX_LENGTH,
        **COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG
    )


class UserDetail(BaseModel):
    """Model to store User Details"""

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    address = models.JSONField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    date_of_birth = models.DateField(**COMMON_BLANK_AND_NULLABLE_FIELD_CONFIG)
    gender = models.CharField(
        choices=GenderChoices.choices, max_length=COMMON_CHAR_FIELD_MAX_LENGTH
    )

    class Meta(BaseModel.Meta):
        default_related_name = "related_user_details"
