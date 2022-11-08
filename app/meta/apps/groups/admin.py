from django.conf import settings
from django.contrib import admin

from .models import StudentGroup
from ..users.choices import GenderUser
from ..users.models import Student


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'count_male',
        'count_female',
        'free_space',
    )

    def free_space(self, obj):
        count_male = StudentGroup.objects.filter(id=obj.id, set_students__gender=GenderUser.MALE).count()
        count_female = StudentGroup.objects.filter(id=obj.id, set_students__gender=GenderUser.FEMALE).count()
        free_space = settings.MAX_PLACES - count_male - count_female
        if not free_space:
            return '0'
        return f'{free_space}'

    def count_male(self, obj):
        count_male = StudentGroup.objects.filter(id=obj.id, set_students__gender=GenderUser.MALE).count()
        if not count_male:
            return '0'
        return f'{count_male}'

    def count_female(self, obj):
        count_female = StudentGroup.objects.filter(id=obj.id, set_students__gender=GenderUser.FEMALE).count()
        if not count_female:
            return '0'
        return f'{count_female}'
