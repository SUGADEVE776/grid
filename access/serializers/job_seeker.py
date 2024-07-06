from rest_framework import serializers

from access.models import User
from common.serializers import (
    AppReadOnlyModelSerializer,
    AppUpdateModelSerializer,
    AppWriteOnlyModelSerializer,
)


class UserCreateModelSerializer(AppWriteOnlyModelSerializer):
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]


class UserListModelSerializer(AppReadOnlyModelSerializer):
    class Meta(AppWriteOnlyModelSerializer.Meta):
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "username",
            "phone_number",
            "type",
        ]
