from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings

phone_validator = RegexValidator(
    r"^\+[1-9]\d{7,14}$",
    "Use international format, for example +251911234567",
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password=None, **extra):
        if not phone:
            raise ValueError("Phone number is required")
        email = extra.pop("email", None)
        user = self.model(
            phone=phone,
            email=self.normalize_email(email) if email else None,
            **extra,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra)


class User(AbstractUser):
    username = None
    phone = models.CharField(max_length=16, unique=True, validators=[phone_validator])
    email = models.EmailField(unique=True, null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name= "addresses" , on_delete =models.CASCADE)
    street = models.CharField(max_length=255)
    apartment = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}"

    