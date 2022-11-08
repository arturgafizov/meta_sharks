import logging
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from . import serializers
from .excel import ExcelFileOperation
from .generators import get_tokens_for_user
from . import swagger_schemas as schemas
from .models import Student
from .tasks import generate_excel_report
from ..directions.models import Direction
from .permissions import IsCurator
from ..groups.models import StudentGroup

User = get_user_model()

logger = logging.getLogger(__name__)


class LoginView(GenericAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = []

    @method_decorator(name='create', decorator=swagger_auto_schema(**schemas.login, ))
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['login']
        user = User.objects.get(email=email)
        return (
            Response(get_tokens_for_user(user), status=status.HTTP_200_OK)
        )


class SignUpView(CreateAPIView):
    permission_classes = []
    serializer_class = serializers.UserSignUpSerializer

    @swagger_auto_schema(**schemas.signup_schema)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)


@method_decorator(name='list', decorator=swagger_auto_schema(**schemas.student_group_list, ))
class StudentViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'delete', 'patch', )
    permission_classes = [IsAuthenticated, IsCurator, ]
    serializer_class = serializers.StudentSerializer

    def get_queryset(self):
        return Student.objects.prefetch_related('student_group').all()

    @method_decorator(name='retrieve', decorator=swagger_auto_schema(**schemas.student_group_retrieve, ))
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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


class AddStudentInGroupView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsCurator, ]
    serializer_class = serializers.AddStudentInGroupView

    @swagger_auto_schema(**schemas.student_add_in_group)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Student added in group successfully'}, status=status.HTTP_200_OK)


class ExportExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsCurator, ]

    @swagger_auto_schema(**schemas.generate_excel_file)
    def get(self, request):
        titles = [('направление подготовки / куратор', 16000),
                  ('название группы /кол-во мужчин /кол-во женщин /кол-во свободных мест. | cтуденты группы', 26000)]
        directions_date = list(Direction.objects.all())
        groups_date = list(StudentGroup.objects.all())
        data = {
            'directions': directions_date,
            'groups_date': groups_date,
        }
        filename = Path('export') / str(datetime.now().date()) / f'{uuid4().hex[16:]}.xlsx'
        url_file = Path(settings.MEDIA_ROOT) / filename
        service = ExcelFileOperation(str(url_file), titles, data)
        file = service.xcl_export()
        return file


class GetExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsCurator, ]

    @swagger_auto_schema(**schemas.get_excel_file)
    def get(self, request):
        excel_task = generate_excel_report.delay()
        data = {
            'task_id': excel_task.task_id,
            'status': excel_task.status,
        }
        return Response(data, status=status.HTTP_200_OK)
