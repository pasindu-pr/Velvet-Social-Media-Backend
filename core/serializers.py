from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer as BaseUserRegisterSerializer
from djoser.serializers import UserSerializer as BaseCurrentUserSerializer

class UserCreateSerializer(BaseUserRegisterSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'birthdate','password', 'location']


class CurrentUserSerializer(BaseCurrentUserSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'birthdate', 'location']