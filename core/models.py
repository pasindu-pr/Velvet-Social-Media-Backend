from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import CharField


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, \
         email, birthdate, password, profile_picture, location):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            birthdate=birthdate,
            first_name=first_name,
            last_name=last_name,
            location=location,
            profile_picture=profile_picture
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


# Create your models here. 
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    birthdate = models.DateField(null=True)
    profile_picture = models.URLField(null=True)
    location = models.CharField(max_length=255, null=True) 
    description = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()