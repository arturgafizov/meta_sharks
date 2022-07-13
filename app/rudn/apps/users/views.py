import logging
import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.contrib.auth import logout as django_logout
from django.utils.translation import gettext_lazy as _
from dj_rest_auth import views as auth_views
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework_simplejwt import serializers as jwt_serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.conf import settings

from . import serializers
from .redis_handler import RedisHandler
from .services import UsersService, full_logout, AuthAppService
from .generators import get_tokens_for_user
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

logger = logging.getLogger(__name__)


class ViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'delete')


class UserModelViewSet(ViewSet):
    serializer_class = serializers.UserSerializer
    # parser_classes = (MultiPartParser, JSONParser, )

    def get_queryset(self):
        return User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDepositSumViewView(ListAPIView):
    serializer_class = serializers.UserDepositSumSerializers

    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        return queryset


class SignUpView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.UserSignUpSerializer


class UserViewSet(GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'change_email':
            return serializers.EmailChangeSerializer
        elif self.action == 'change_password':
            return serializers.ChangePasswordSerializer
        elif self.action == 'change_username':
            return serializers.ChangeUsernameSerializer

    def change_email(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('New email has been saved')})

    def change_password(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.session['new_password'] = serializer.validated_data['password1']
        serializer.save()
        return Response({'detail': _('To save a new password, click on the link sent to your email')})

    def change_username(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': _('New username has been saved')})


class PasswordResetTokenView(GenericAPIView):
    serializer_class = serializers.ValidatePasswordTokenSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK
        )


class PasswordResetTokenConfirmView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Password has been reset with the new password.")}
        )


class ChangePasswordConfirmView(GenericAPIView):
    serializer_class = serializers.ChangePasswordConfirmSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("User was activated by the link when changing the password.")}
        )


class VerifyEmailView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.VerifyEmailSerializer

    # @swagger_auto_schema(**schemas.signup_verify_schema)
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'ok'}, status=status.HTTP_200_OK)


class PreLoginView(GenericAPIView):
    serializer_class = serializers.PreLoginSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['login']
        request.session['email'] = email
        serializer.save()
        return Response(
            {'detail': _('We have sent email with code to your number, code will be expired 20 minutes')},
            status=status.HTTP_200_OK,
        )

# class PreLoginView(GenericAPIView):
#     serializer_class = serializers.PreLoginSerializer
#     permission_classes = []
#
#     def post(self, request):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         email = serializer.validated_data['login']
#         request.session['email'] = email
#         print(email)
#         user = AuthAppService.get_user(email)
#         ControlsService.make_session(request, user)
#         return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


class LoginView(GenericAPIView):
    serializer_class = serializers.LoginSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(get_tokens_for_user(user), status=status.HTTP_200_OK)


class LogoutView(auth_views.LogoutView):
    allowed_methods = ('POST', 'OPTIONS')

    def post(self, request, *args, **kwargs):
        user = request.user
        return self.logout(request)

    def session_logout(self):
        django_logout(self.request)

    def logout(self, request):
        self.session_logout()
        response = full_logout(request)
        return response


class CurrentUserView(APIView):

    def get(self, request):
        user = request.user
        serializer = serializers.CurrentUserSerializers(user)
        return Response(serializer.data)


