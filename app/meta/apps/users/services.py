import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .decorators import except_shell
from .models import Student
from ..groups.models import StudentGroup

User = get_user_model()


class AuthAppService:

    @staticmethod
    def validate_email(email: str):
        re_email = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,30})+$'
        if not re.search(re_email, email):
            return False, _("Entered email address is not valid")
        return True, ''

    @staticmethod
    def is_email_exists(email: str) -> bool:
        return User.objects.filter(email=email).exists()

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user(email: str):
        return User.objects.get(email=email)


class UsersService:

    @staticmethod
    @except_shell((Student.DoesNotExist,))
    def get_student(email: str) -> Student:
        return Student.objects.get(email=email)

    @staticmethod
    def make_user_active(user):
        user.is_active = True
        user.save(update_fields=['is_active'])
        return user

    @staticmethod
    def check_student_group(group_name: str, email: str):
        return StudentGroup.objects.filter(title=group_name, set_students__email=email).exists()

    @staticmethod
    def get_file_url_and_file_root(directory: str):
        filename = Path(directory) / str(datetime.now().date()) / f'{uuid4().hex[16:]}.xlsx'
        return Path(settings.MEDIA_ROOT) / filename
