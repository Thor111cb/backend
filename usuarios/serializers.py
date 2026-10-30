from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class RegistroSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden."
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        usuario = Usuario.objects.create_user(
            **validated_data,
            rol="cliente"
        )

        return usuario