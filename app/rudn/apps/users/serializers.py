import json
from datetime import timedelta

from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from urllib.parse import urljoin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode, urlencode
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .generators import gen_security_code
from .models import IdentificationCode
from .services import AuthAppService, UsersService
from .tasks import send_information_email
from .backends import EmailBackend


User = get_user_model()

error_messages = {
    'not_verified': _('Email not verified'),
    'not_active': _('Your account is not active. Please contact Your administrator'),
    'wrong_credentials': _('Entered email or password is incorrect'),
}


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'keyword', 'email', 'username', 'available_usdt', 'in_orders_usdt',
                  'available_swht', 'in_deposit_swht', 'available_btc')

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        instance.sum_usdt = instance.available_usdt + instance.in_orders_usdt
        instance.sum_swht = instance.available_swht + instance.in_deposit_swht
        instance.save()
        return instance


class UserSignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=2, max_length=100, required=True)
    password1 = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    keyword = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password1', 'password2', 'keyword')

    def validate_password1(self, password: str) -> str:
        validate_password(password)
        return password

    def validate_email(self, email) -> str:
        status, msg = AuthAppService.validate_email(email)
        if not status:
            raise serializers.ValidationError(msg)
        if email and email_address_exists(email):
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
        request = self.context['request']
        self.validated_data['password'] = self.validated_data.pop('password1')
        del self.validated_data['password2']
        user = User.objects.create_user(**self.validated_data, is_active=False)
        setup_user_email(request=request, user=user, addresses=[])
        UsersService.send_email_confirm(request, user)
        return user


class EmailChangeSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=128)
    repeat_email = serializers.CharField(max_length=128)
    keyword = serializers.CharField(max_length=20)

    class Meta:
        model = User
        fields = ('email', 'repeat_email', 'keyword')

    def validate_email(self, email) -> str:
        status, msg = AuthAppService.validate_email(email)
        if not status:
            raise serializers.ValidationError(msg)
        if email and email_address_exists(email):
            raise serializers.ValidationError(_("User is already registered with this e-mail address."))
        return email

    def validate(self, data):
        if data['email'] != data['repeat_email']:
            raise serializers.ValidationError({'repeat_email': _("The two email fields didn't match.")})
        return data

    def save(self):
        user = self.context.get('request').user
        user.email = self.validated_data['email']
        user.save(update_fields=['email'])
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    password1 = serializers.CharField(max_length=128)
    password2 = serializers.CharField(max_length=128)

    def get_reset_url(self, uid, token):
        query_params = urlencode({'uid': uid, 'token': token})
        path = f'/change-password/confirm?{query_params}'
        url = urljoin(path, path)
        return settings.FRONTEND_SITE + str(url)

    def validate_old_password(self, password: str) -> str:
        user = self.context.get('request').user
        if not user.check_password(password):
            raise serializers.ValidationError(_('Your old password incorrect'))
        return password

    def validate_password1(self, password: str) -> str:
        validate_password(password)
        return password

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({'password2': _("The two password fields didn't match.")})
        return data

    def save(self):
        user = self.context.get('request').user
        self.context.get('request').session['new_password'] = self.validated_data['password1']
        uid: str = urlsafe_base64_encode(smart_bytes(user.id))
        token: str = PasswordResetTokenGenerator().make_token(user)
        if not user:
            raise ValidationError({'email': _('User does not exist with this email')})
        url = self.get_reset_url(uid=uid, token=token)
        print(url)
        data = {
            'subject': _("Confirm your password"),
            'template_name': 'emails/change_password.html',
            'to_email': user.email,
            'context': {
                'user': user.full_name(),
                'reset_url': url,
            }
        }
        send_information_email.delay(**data)

        return user


class ChangeUsernameSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)

    def validate(self, data):
        username = data['username']
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({'username': _(f'User is already exist with username - {username}')})
        return data

    def save(self):
        user = self.context.get('request').user
        user.username = self.validated_data['username']
        user.save(update_fields=['username'])
        return user


class ValidatePasswordTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def get_reset_url(self, uid, token):
        query_params = urlencode({'uid': uid, 'token': token})
        path = f'/password-reset/confirm?{query_params}'
        url = urljoin(path, path)
        return settings.FRONTEND_SITE + str(url)

    def save(self):
        """
        Generate a one-use only link for resetting password and send it to the user.
        """
        user = AuthAppService.get_user(email=self.validated_data['email'])
        if not user:
            raise ValidationError({'email': _('User does not exist with this email')})
        uid: str = urlsafe_base64_encode(smart_bytes(user.id))
        token: str = PasswordResetTokenGenerator().make_token(user)

        url = self.get_reset_url(uid=uid, token=token)

        data = {
            'subject': _("Confirm your password"),
            'template_name': 'emails/index_password.html',
            'to_email': user.email,
            'context': {
                'user': user.full_name(),
                'reset_url': url,
                'frontend_site': settings.FRONTEND_SITE,
            }
        }
        send_information_email.delay(**data)


class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        service = UsersService()
        self.user = service.check_reset_token(attrs['uid'], attrs['token'])
        return attrs

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()


class ChangePasswordConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        service = UsersService()
        self.user = service.check_reset_token(attrs['uid'], attrs['token'])
        return attrs

    def save(self):
        print(self.context.get('request').session.items())
        new_password = self.context['request'].session['new_password']
        self.user.set_password(new_password)
        self.user.save(update_fields=['password'])
        self.user.save()


class VerifyEmailSerializer(serializers.Serializer):
    key = serializers.CharField()


class PreLoginSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=128)
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

    def save(self, **kwargs):
        code = gen_security_code()
        print(code)
        IdentificationCode.objects.create(user=self.user, code=code)
        AuthAppService.send_security_code_email(self.user, code)


class LoginSerializer(serializers.Serializer):
    code = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, attrs: dict):
        try:
            ident_code = IdentificationCode.objects.get(user__email=attrs['email'], code=attrs['code'])
        except IdentificationCode.DoesNotExist:
            raise serializers.ValidationError({'Error': _("The code is invalid")})

        if not ident_code.active:
            raise serializers.ValidationError({'Error': _("The code is not active")})

        code_lifetime = ident_code.time_created + timedelta(minutes=20)
        if code_lifetime < now():
            raise serializers.ValidationError({'Error': _("The code is expired")})

        ident_code.active = False
        ident_code.save()
        return ident_code.user


class UserDepositSumSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('sum_swht', 'available_swht', 'in_deposit_swht')


class CurrentUserSerializers(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', )

