from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Direction(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование направления', unique=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='set_directions')

    objects = models.Manager()

    def __str__(self):
        return f'{self.title}'

    @property
    def tutor_date(self):
        email = self.user
        user = User.objects.get(email=email)
        return f'{user.first_name} {user.last_name} {email}'


class Subject(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(verbose_name='Описание учебного предмета')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='directions')
    objects = models.Manager()

    def __str__(self):
        return self.name
