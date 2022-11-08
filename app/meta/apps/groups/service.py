from django.conf import settings

from .models import StudentGroup
from ..users.choices import GenderUser
from ..users.decorators import except_shell


class GroupService:

    @staticmethod
    def get_group_free_place(group_name: str) -> int:
        count_male = StudentGroup.objects.filter(title=group_name, set_students__gender=GenderUser.MALE).count()
        count_female = StudentGroup.objects.filter(title=group_name, set_students__gender=GenderUser.FEMALE).count()
        free_space = settings.MAX_PLACES - count_male - count_female
        return free_space

    @staticmethod
    @except_shell((StudentGroup.DoesNotExist,))
    def get_student_group(group_name: str) -> StudentGroup:
        return StudentGroup.objects.get(title=group_name)
