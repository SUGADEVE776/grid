from access.config import UserTypeChoices
from access.models import User
from common.serializers import AppCreateModelSerializer


class RecruiterUserCreateSerializer(AppCreateModelSerializer):
    class Meta(AppCreateModelSerializer.Meta):
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone_number",
        ]

    def validate(self, attrs):
        attrs["type"] = UserTypeChoices.recruiter
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
