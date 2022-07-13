from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import RedirectView
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

app_name = 'apps.users'

router = DefaultRouter()
# router.register('user', views.UserModelViewSet, basename='user')


urlpatterns = [
    path('', login_required(RedirectView.as_view(pattern_name='admin:index'))),
    path('current-user/', views.CurrentUserView.as_view(), name='current_user'),
    path('pre-login/', views.PreLoginView.as_view(), name='api_pre-login'),
    path('login/', views.LoginView.as_view(), name='api-login'),
    path('register/', views.SignUpView.as_view(), name='api_sign_up'),
    path('register/verify', views.VerifyEmailView.as_view(), name='api_sign_up_verify'),
    path('update/email/', views.UserViewSet.as_view({'post': 'change_email'}), name='change_email'),
    path('update/password/', views.UserViewSet.as_view({'post': 'change_password'}), name='change_password'),
    path('update/password/confirm/', views.ChangePasswordConfirmView.as_view(), name='change_password_confirm'),
    path('update/username/', views.UserViewSet.as_view({'post': 'change_username'}), name='change_username'),
    path('password/reset/', views.PasswordResetTokenView.as_view(), name='forgot_password'),
    path('password/reset/confirm/', views.PasswordResetTokenConfirmView.as_view(), name='password_reset_confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

]


urlpatterns += router.urls
