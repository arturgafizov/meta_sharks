from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):

    email = models.EmailField(_('Email address'), unique=True)
    keyword = models.CharField(max_length=200)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email

    def full_name(self):
        return super().get_full_name()

    def user_active_quantity(self):
        users = User.objects.all()
        return users.filter(is_active=True).count()

    def delete(self, **kwargs):
        self.outstandingtoken_set.all().delete()
        return super().delete(**kwargs)


class IdentificationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('User'))
    code = models.CharField(_('Code'), max_length=10)
    active = models.BooleanField(_('Active'), default=True)
    time_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Time created'))
    objects = models.Manager()

