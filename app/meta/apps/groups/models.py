from django.conf import settings
from django.db import models

from ..users.choices import GenderUser


class StudentGroup(models.Model):
    title = models.CharField(max_length=128, verbose_name='Наименование группа', unique=True)
    objects = models.Manager()

    def __str__(self):
        return f'{self.title}    / {self.get_count_male}    / {self.get_count_female}   /  {self.get_free_space} | ' \
               f'{self.get_students_group}'

    @property
    def get_count_male(self) -> int:
        return self.set_students.filter(gender=GenderUser.MALE).count()

    @property
    def get_count_female(self) -> int:
        return self.set_students.filter(gender=GenderUser.FEMALE).count()

    @property
    def get_free_space(self) -> int:
        count_male = self.set_students.filter(gender=GenderUser.MALE).count()
        count_female = self.set_students.filter(gender=GenderUser.FEMALE).count()
        free_space = settings.MAX_PLACES - count_male - count_female
        return free_space

    @property
    def get_students_group(self):
        return list(self.set_students.all().order_by('last_name'))
