import secrets
import string
from datetime import timedelta
from django.db.models import Q
from django.utils.timezone import now
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token, BlacklistMixin
from django.contrib.auth import get_user_model

from .models import IdentificationCode
from .redis_handler import RedisHandler

User =get_user_model


def gen_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(8))


def gen_security_code():
    alphabet = string.digits
    return ''.join(secrets.choice(alphabet) for i in range(4))


def cleaning_expired_codes():
    week_ago = now() - timedelta(days=7)
    codes = IdentificationCode.objects.all()
    expired_codes = codes.filter(Q(active=False) | Q(active=True, time_created__lte=week_ago))
    expired_codes.delete()


class AccessToken(Token):
    token_type = 'access'

    @property
    def lifetime(self):
        redis = RedisHandler()
        return timedelta(minutes=redis.get_login_downtime())


class AdminAccessToken(AccessToken):

    @property
    def lifetime(self):
        redis = RedisHandler()
        return timedelta(minutes=redis.get_admin_login_downtime())


class RefreshToken(BlacklistMixin, Token):
    token_type = 'refresh'
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        'exp',

        api_settings.JTI_CLAIM,
        'jti',
    )

    access_token_class = AccessToken

    @property
    def access_token(self):
        access = self.access_token_class()
        access.set_exp(from_time=self.current_time)
        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value
        return access


class AdminRefreshToken(RefreshToken):
    access_token_class = AdminAccessToken


def get_tokens_for_user(user):
    if user.is_staff:
        refresh = AdminRefreshToken.for_user(user)
    else:
        refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'lifetime_refresh': refresh.lifetime,
        'lifetime_access': refresh.access_token.lifetime,
    }
