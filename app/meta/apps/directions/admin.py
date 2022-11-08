from django.contrib import admin

from .models import Direction, Subject


class SubjectInline(admin.TabularInline):
    model = Subject
    extra = 0


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'user',
    )
    inlines = [SubjectInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'created_at',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('direction')
