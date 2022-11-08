from django.contrib import admin
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Student, User


@admin.register(Student)
class CustomStudentAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('first_name', 'email', 'is_active', 'phone', 'gender')
    search_fields = ('first_name', 'last_name', 'email', )
    list_filter = ('is_active', 'phone')
    list_editable = ('is_active', 'gender')
    list_per_page = 20

    fieldsets = (
        (_('Personal info'), {'fields': ('id', 'first_name', 'last_name', 'email', 'student_group', 'gender')}),
        (_('Permissions'), {
            'fields': ('is_active',),
        }),

    )
    readonly_fields = ('id',)
    filter_horizontal = ['student_group']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('student_group').all()


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    ordering = ('-id',)
    list_display = ('email', 'is_active', 'phone', 'role')
    search_fields = ('first_name', 'last_name', 'email', )
    list_filter = ('is_active', 'phone')
    list_editable = ('is_active', 'role')
    list_per_page = 20

    fieldsets = (
        (_('Personal info'), {'fields': ('id', 'first_name', 'last_name', 'email', 'password', 'username', 'role')}),
        (_('Permissions'), {
            'fields': ('is_active',),
        }),

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('id',)



title = settings.MICROSERVICE_TITLE

admin.site.site_title = title
admin.site.site_header = title
admin.site.site_url = '/'
admin.site.index_title = title

admin.site.unregister(Group)
# admin.site.unregister(OutstandingToken)
# admin.site.register(OutstandingToken)
