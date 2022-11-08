from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .backends import EmailBackend
from .services import AuthAppService, UsersService
from ..groups.models import StudentGroup
from ..groups.service import GroupService
from .models import Student

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'is_active', 'email', 'address', 'phone', 'gender')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'role', 'password')


class LoginSerializer(serializers.Serializer):
    login = serializers.EmailField(min_length=2, max_length=100, required=True)
    password = serializers.CharField(max_length=128)

    def validate(self, attrs: dict):
        self.user = self.authenticate(login=attrs['login'], password=attrs['password'])
        if self.user is None:
            raise serializers.ValidationError({'Error': _("The credentials is invalid")})
        if not self.user.is_active:
            raise serializers.ValidationError({'Error': _("The user is not active")})
        return attrs

    def authenticate(self, **kwargs):
        back = EmailBackend()
        return back.authenticate(**kwargs)


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=2, max_length=100, required=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password1', 'password2', 'role')

    def validate_password1(self, password: str) -> str:
        validate_password(password)
        return password

    def validate_email(self, email) -> str:
        status, msg = AuthAppService.validate_email(email)
        if not status:
            raise serializers.ValidationError(msg)
        if email and AuthAppService.is_email_exists(email):
            raise serializers.ValidationError(_("User is already registered with this e-mail address."))
        return email

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': _("The two password fields didn't match.")})
        username = data['username']
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _(f'User is already exist with username - {username}')})
        return data

    def save(self):
        self.validated_data['password'] = self.validated_data.pop('password1')
        del self.validated_data['password2']
        user = User.objects.create_user(**self.validated_data, is_active=True)
        return user


class AddStudentInGroupView(serializers.Serializer):
    student = serializers.EmailField(min_length=2, max_length=100, required=True)
    group_name = serializers.CharField(max_length=100)

    def validate(self, data):
        student = UsersService.get_student(data['student'])
        if UsersService.check_student_group(data['group_name'], student.email):
            raise serializers.ValidationError(
                {'Error': _("This student is already in this group")})
        if not student:
            raise serializers.ValidationError(
                {'Error': _("This student is not found")})
        group = GroupService.get_student_group(data['group_name'])
        if not group:
            raise serializers.ValidationError(
                {'Error': _("This group is not found")})
        group_name = data['group_name']
        free_place = GroupService.get_group_free_place(group_name)
        if free_place <= 0:
            raise serializers.ValidationError(
                {'Error': _("This group is not free place")})
        return data

    def create(self, validated_data):
        group_name = validated_data.get('group_name')
        email = validated_data.get('student')
        student = Student.objects.get(email=email)
        group = StudentGroup.objects.get(title=group_name)
        student.student_group.add(group)
        return group
