import re

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from urllib.parse import urljoin
from django.conf import settings
import urllib.request
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from .decorators import except_shell
from .tasks import send_information_email


User = get_user_model()


class AuthAppService:

    @staticmethod
    def validate_email(email):
        re_email = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,30})+$'
        if not re.search(re_email, email):
            return False, _("Entered email address is not valid")
        return True, ''

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user(email):
        return User.objects.get(email=email)

    @staticmethod
    @except_shell((User.DoesNotExist,))
    def get_user_by_id(user_id: int):
        return User.objects.get(id=user_id)

    @staticmethod
    def send_security_code_email(user, code):
        subject = _("Code for authorization")
        html_email_template_name = 'emails/temp_code.html'
        print('CODE', code)
        context = {
            'code': f'Код для авторизации: {code}'
        }
        to_email = user.email
        return send_information_email.delay(subject, html_email_template_name, context, to_email)


class UsersService:

    @staticmethod
    def send_email_confirm(request, user):
        # url = AuthAppService.get_activate_url(user)
        subject = _("Confirm your email")
        html_email_template_name = 'emails/index_registration.html'
        context = {
            # 'activate_url': url,
            'frontend_site': settings.FRONTEND_SITE,
        }
        to_email = user.email
        send_information_email.delay(subject, html_email_template_name, context, to_email)



    @staticmethod
    def check_reset_token(uid: str, token: str):
        try:
            pk = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=pk)
            print("_CHECK_", user)
        except (ValueError, User.DoesNotExist):
            raise ValidationError({'uid': 'uid is not valid, please request a new one'})
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise ValidationError({'token': 'Token is not valid, please request a new one'})
        return user

    @staticmethod
    def make_user_active(user):
        user.is_active = True
        user.save(update_fields=['is_active'])
        return user


def full_logout(request):
    response = Response({"detail": _("Successfully logged out.")}, status=HTTP_200_OK)
    if cookie_name := getattr(settings, 'JWT_AUTH_COOKIE', None):
        response.delete_cookie(cookie_name)
    refresh_cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
    refresh_token = request.COOKIES.get(refresh_cookie_name)
    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name)
    if 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
        # add refresh token to blacklist
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except KeyError:
            response.data = {"detail": _("Refresh token was not included in request data.")}
            response.status_code = HTTP_401_UNAUTHORIZED
        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, 'args'):
                if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                    response.data = {"detail": _(error.args[0])}
                    response.status_code = HTTP_401_UNAUTHORIZED
                else:
                    response.data = {"detail": _("An error has occurred.")}
                    response.status_code = HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {"detail": _("An error has occurred.")}
                response.status_code = HTTP_500_INTERNAL_SERVER_ERROR

    else:
        message = _(
            "Neither cookies or blacklist are enabled, so the token "
            "has not been deleted server side. Please make sure the token is deleted client side."
        )
        response.data = {"detail": message}
        response.status_code = HTTP_200_OK
    return response
