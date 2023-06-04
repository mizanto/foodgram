from djoser.serializers import UserCreateSerializer as DefaultUserCreateSerializer
from django.contrib.auth import get_user_model


class UserCreateSerializer(DefaultUserCreateSerializer):
    class Meta(DefaultUserCreateSerializer.Meta):
        model = get_user_model()
        fields = ['email', 'username', 'first_name', 'last_name', 'password']
