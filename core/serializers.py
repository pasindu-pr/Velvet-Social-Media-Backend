from djoser.serializers import UserCreateSerializer as BaseUserRegisterSerializer
from django.contrib.auth import get_user_model

class UserCreateSerializer(BaseUserRegisterSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'birthdate','password', 'location']