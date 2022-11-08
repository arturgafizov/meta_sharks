from django.db.models import TextChoices


class GenderUser(TextChoices):
    MALE = ('male', 'мужчина')
    FEMALE = ('female', 'женщина')


class StatusUser(TextChoices):
    ADMIN = ('admin', 'администратор')
    CURATOR = ('curator', 'куратор')
