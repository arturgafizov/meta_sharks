from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from .choices import StatusUser


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        print(request.user.role)
        if request.user.role == StatusUser.ADMIN:
            return True
        else:
            raise PermissionDenied('Вы не можете управлять сущностями Направление подготовки и Учебная дисциплина.')


class IsCurator(BasePermission):

    def has_permission(self, request, view):
        print(request.user.role)
        if request.user.role == StatusUser.CURATOR:
            return True
        else:
            raise PermissionDenied('Вы не можете управлять сущностями Студент и Учебная группа.')
