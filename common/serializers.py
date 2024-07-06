from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.serializers import ModelSerializer, Serializer

from common import model_fields
from common.config import CUSTOM_ERRORS_MESSAGES
from common.helpers import get_display_name_for_slug, get_first_of, unpack_dj_choices
from common.model_fields import AppFileField, AppImageField
from common.models import BaseModel


class CustomErrorMessagesMixin:
    """
    Overrides the constructor of the serializer to add meaningful error
    messages to the serializer output. Also used to hide security
    related messages to the user.
    """

    def get_display(self, field_name):
        return field_name.replace("_", " ")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # adding custom error messages
        for field_name, field in getattr(self, "fields", {}).items():
            if field.__class__.__name__ == "ManyRelatedField":
                # many-to-many | uses foreign key field for children
                field.error_messages.update(CUSTOM_ERRORS_MESSAGES["ManyRelatedField"])
                field.child_relation.error_messages.update(
                    CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"]
                )
            elif field.__class__.__name__ == "PrimaryKeyRelatedField":
                # foreign-key
                field.error_messages.update(
                    CUSTOM_ERRORS_MESSAGES["PrimaryKeyRelatedField"]
                )
            else:
                # other input-fields
                field.error_messages.update(
                    {
                        "blank": f"Please enter your {self.get_display(field_name)}",
                        "null": f"Please enter your {self.get_display(field_name)}",
                    }
                )


class AppSerializer(Serializer):
    """
    The app's version for the Serializer class. Just to implement common and
    other verifications and schema. Used only for light weight stuff.
    """

    def get_initial_data(self, key, expected_type):
        """
        Central function to get the initial data without breaking. We might
        expect a string, but user gave None. The given expected_type
        is what the type of data the caller is expecting.
        """

        _data = self.initial_data.get(key)

        if type(_data) != expected_type:
            raise SkipField()

        return _data

    def get_user(self):
        """Return the user from the request."""

        return self.get_request().user

    def get_request(self):
        """Returns the request."""

        return self.context["request"]


class AppModelSerializer(AppSerializer, ModelSerializer):
    """
    Applications version of the ModelSerializer. There are separate serializers
    defined for handling the read and write operations separately.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta:
        pass

    def serialize_dj_choices(self, choices: dict):
        """
        Given a list of choices like:
            {'open': <Choice[1]:Open>, 'in_progress': <Choice[2]:In Progress>, ...}

        This will return the following:
            [{'id': 'open', 'identity': 'Open'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        return unpack_dj_choices(choices)

    def serialize_for_meta(self, queryset, fields=None):
        """Central serializer for the `get_meta`. Just a dry function."""

        if not fields:
            fields = ["id"]

        return simple_serialize_queryset(fields=fields, queryset=queryset)


class AppWriteOnlyModelSerializer(AppModelSerializer):
    """
    Write only version of the `AppModelSerializer`. Does not support read
    operations and to_representations. Validations are implemented here.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    def create(self, validated_data):
        """Overridden to set the `created_by` field."""

        instance = super().create(validated_data=validated_data)

        # setting the anonymous fields
        if hasattr(instance, "created_by") and not instance.created_by:
            user = self.get_user()

            instance.created_by = user if user and user.is_authenticated else None
            instance.save()

        return instance

    def update(self, instance, validated_data):
        """Overridden to set the `modified_by` field."""

        instance = super().update(instance, validated_data)

        # setting the anonymous fields
        if hasattr(instance, "modified_by"):
            user = self.get_user()

            instance.modified_by = user if user and user.is_authenticated else None
            instance.save()

        return instance

    def get_validated_data(self, key=None):
        """Central function to return the validated data."""

        return self.validated_data[key] if key else self.validated_data

    def __init__(self, *args, **kwargs):
        # all fields are required
        for field in self.Meta.fields:
            self.Meta.extra_kwargs.setdefault(field, {})
            self.Meta.extra_kwargs[field]["required"] = True

        super().__init__(*args, **kwargs)

    class Meta(AppModelSerializer.Meta):
        model = None
        fields = []
        extra_kwargs = {}

    def to_internal_value(self, data):
        """Overridden to pre-process inbound data."""

        data = super().to_internal_value(data=data)

        # blank values are not allowed in our application | convert to null
        for k, v in data.items():
            if not v and v not in [False, 0, []]:
                data[k] = None

        return data

    def to_representation(self, instance):
        """Always show the updated data from instance back to the front-end."""

        return self.get_meta_initial()

    def serialize_choices(self, choices: list):
        """
        Given a list of choices like:
            ['active', ...]

        This will return the following:
            [{'id': 'active', 'identity': 'Active'}, ...]

        This will be convenient for the front end to integrate. Also
        this is considered as a standard.
        """

        from apps.common.helpers import get_display_name_for_slug

        return [{"id": _, "identity": get_display_name_for_slug(_)} for _ in choices]

    def get_dynamic_render_config(self):
        """
        Returns a config that can be used by the front-end to dynamically
        render and handle the form fields. This improves delivery speed.
        """

        from apps.common.models import BaseUploadModel
        from django.db import models

        model = self.Meta.model
        render_config = []

        for _ in self.get_fields():
            model_field = model.get_model_field(_, fallback=None)

            field_type = "UNKNOWN_CONTACT_DEVELOPER"
            other_config = {}

            if model_field:
                # type
                try:
                    if isinstance(model_field, models.ForeignKey) and issubclass(
                        model_field.related_model, BaseUploadModel
                    ):
                        if "image" in _:
                            field_type = "ImageUpload"
                        else:
                            field_type = "FileUpload"
                    elif (
                        isinstance(model_field, models.CharField)
                        and model_field.choices
                    ):
                        field_type = "ChoiceField"
                    else:
                        field_type = model_field.__class__.__name__

                except Exception as e:
                    print(e)  # noqa

                # other render config
                try:
                    other_config["label"] = get_display_name_for_slug(
                        get_first_of(model_field.verbose_name, _)
                    )
                    other_config["help_text"] = get_first_of(model_field.help_text)
                    other_config["allow_null"] = model_field.null
                except Exception as e:
                    print(e)  # noqa

            render_config.append(
                {
                    "key": _,
                    "type": field_type,
                    "other_config": other_config,
                }
            )

        return render_config

    def get_meta(self) -> dict:
        """
        Returns the meta details for `get_meta_for_create` & `get_meta_for_update`.
        This is just a centralized function.
        """

        return {}

    def get_meta_for_create(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": {},
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_for_update(self):
        """
        Returns the necessary meta details for front-end. Overridden
        on the child classes. Called from view.
        """

        return {
            "meta": self.get_meta(),
            "initial": self.get_meta_initial(),
            "render_config": self.get_dynamic_render_config(),
        }

    def get_meta_initial(self):
        """
        Returns the `initial` data for `self.get_meta_for_update`. This is
        used by the front-end for setting initial values.
        """

        instance = self.instance
        initial = {}
        for field_name in ["id", *self.fields.keys()]:
            if field_name == "password":
                initial[field_name] = None
            else:
                initial[field_name] = getattr(instance, field_name, None)

        # simplify for FE
        for k, v in initial.items():
            # foreignkey
            if hasattr(initial[k], "pk"):
                initial[k] = v.pk

            # not a model field
            if not instance.__class__.get_model_field(k, None):
                continue

            field = self.Meta.model.get_model_field(k)
            related_model = field.related_model

            field_instance = getattr(self.instance, k)

            # file url for fk instance
            if (
                related_model
                and issubclass(related_model, BaseModel)
                and getattr(self.instance, k)
            ):
                file_model_fields = related_model._meta.fields
                for file_model_field in file_model_fields:
                    if related_model._meta.get_field(
                        file_model_field.name
                    ).__class__ in [AppImageField, AppFileField]:
                        initial[k] = {
                            "id": field_instance.id,
                            file_model_field.name: getattr(
                                field_instance, file_model_field.name
                            ).url,
                        }

            # file or image
            if instance.__class__.get_model_field(k).__class__ in [
                AppImageField,
                AppFileField,
            ]:
                initial[k] = getattr(instance, k).url if getattr(instance, k) else None

            # many-to-many
            if instance.__class__.get_model_field(k).many_to_many:
                initial[k] = getattr(instance, k).values_list("pk", flat=True)

            if (
                instance.__class__.get_model_field(k).__class__
                == model_fields.AppPhoneNumberField
            ):
                initial[k] = (
                    getattr(instance, k).raw_input if getattr(instance, k) else None
                )

        return initial


class AppCreateModelSerializer(AppWriteOnlyModelSerializer):
    """
    Applications version of the CreateModelSerializer which supports only model creation.
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        pass

    def update(self, instance, validated_data):
        """This serializer is only for creation."""

        raise NotImplementedError


class AppUpdateModelSerializer(AppWriteOnlyModelSerializer):
    """
    Applications version of the UpdateModelSerializer which supports only model updates.
    """

    class Meta(AppWriteOnlyModelSerializer.Meta):
        pass

    def create(self, validated_data):
        """This serializer is only for updating."""

        raise NotImplementedError


class AppReadOnlyModelSerializer(AppModelSerializer):
    """
    Read only version of the `AppModelSerializer`. Does not
    support write operations.

    Note:
        Never mix the `read` and `write` serializers, handle them separate.
    """

    class Meta(AppModelSerializer.Meta):
        pass

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
