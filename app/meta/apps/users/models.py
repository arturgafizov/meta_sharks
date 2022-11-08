from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager
from .choices import GenderUser, StatusUser
from ..groups.models import StudentGroup


class Student(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=False)
    email = models.EmailField(unique=True, verbose_name='Почта')
    address = models.CharField(max_length=256, null=True, verbose_name='Адрес')
    phone = PhoneNumberField(unique=True, null=True, blank=True, verbose_name='Мобильный телефон')
    gender = models.CharField(choices=GenderUser.choices, max_length=10)
    student_group = models.ManyToManyField(StudentGroup, related_name='set_students', blank=True)

    objects = UserManager()

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    def __str__(self):
        return f'{self.full_name} {self.email} '


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name='Почта')
    address = models.CharField(max_length=256, null=True, verbose_name='Адрес')
    phone = PhoneNumberField(unique=True, null=True, blank=True, verbose_name='Мобильный телефон')
    role = models.CharField(choices=StatusUser.choices, max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def delete(self, **kwargs):
        self.outstandingtoken_set.all().delete()
        return super().delete(**kwargs)
