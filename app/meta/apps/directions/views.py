from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import serializers
from .models import Direction, Subject
from . import swagger_schemas as schemas
from ..users.permissions import IsAdmin


@method_decorator(name='list', decorator=swagger_auto_schema(**schemas.direction_list, ))
class DirectionViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'delete', 'patch')
    permission_classes = [IsAuthenticated, IsAdmin, ]
    serializer_class = serializers.DirectionsSerializers

    def get_queryset(self):
        return Direction.objects.select_related('subject').all()

    @method_decorator(name='retrieve', decorator=swagger_auto_schema(**schemas.direction_retrieve, ))
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @method_decorator(name='create', decorator=swagger_auto_schema(**schemas.direction_create, ))
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(name='update', decorator=swagger_auto_schema(**schemas.direction_update, ))
    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='partial_update', decorator=swagger_auto_schema(**schemas.direction_partial_update))
    def partial_update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='destroy', decorator=swagger_auto_schema(**schemas.direction_destroy, ))
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(name='list', decorator=swagger_auto_schema(**schemas.subject_list, ))
class SubjectViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'delete', 'patch', )
    permission_classes = [IsAuthenticated, IsAdmin, ]
    serializer_class = serializers.SubjectSerializers

    def get_queryset(self):
        return Subject.objects.all()

    @method_decorator(name='retrieve', decorator=swagger_auto_schema(**schemas.subject_retrieve, ))
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @method_decorator(name='create', decorator=swagger_auto_schema(**schemas.subject_create, ))
    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @method_decorator(name='update', decorator=swagger_auto_schema(**schemas.subject_update, ))
    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='partial_update', decorator=swagger_auto_schema(**schemas.subject_partial_update))
    def partial_update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @method_decorator(name='destroy', decorator=swagger_auto_schema(**schemas.subject_destroy, ))
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddCuratorInDirectionView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdmin, ]
    serializer_class = serializers.AddCuratorInDirectionSerializer

    @swagger_auto_schema(**schemas.add_curator_direction)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Curator added in direction successfully'}, status=status.HTTP_200_OK)
