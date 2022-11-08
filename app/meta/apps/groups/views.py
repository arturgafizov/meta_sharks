from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import serializers
from .models import StudentGroup
from . import swagger_schemas as schemas
from ..users.permissions import IsCurator


class ViewSet(ModelViewSet):
    http_method_names = ('post', 'put', 'delete', 'patch')


class StudentGroupViewSet(ViewSet):
    permission_classes = [IsAuthenticated, IsCurator, ]
    serializer_class = serializers.StudentGroupSerializers

    def get_queryset(self):
        return StudentGroup.objects.prefetch_related('set_students').all()
    # @method_decorator(name='retrieve', decorator=swagger_auto_schema(**schemas.student_group_retrieve, ))
    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    @method_decorator(name='create', decorator=swagger_auto_schema(**schemas.student_group_create, ))
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(name='update', decorator=swagger_auto_schema(**schemas.student_group_update, ))
    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='partial_update', decorator=swagger_auto_schema(**schemas.student_group_partial_update))
    def partial_update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='destroy', decorator=swagger_auto_schema(**schemas.student_group_destroy, ))
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentGroupListSerializer(ListAPIView):
    permission_classes = [IsAuthenticated, IsCurator, ]
    serializer_class = serializers.StudentGroupListSerializers

    @swagger_auto_schema(**schemas.student_group_list)
    def get(self):
        return StudentGroup.objects.prefetch_related('set_students').all()
