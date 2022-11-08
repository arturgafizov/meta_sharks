from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from . import views

app_name = 'apps.users'

router = DefaultRouter()
router.register('student', views.StudentViewSet, basename='student')


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='api-login'),
    path('sign-up/', views.SignUpView.as_view(), name='api-sign-up'),
    path('add-student-group/', views.AddStudentInGroupView.as_view(), name='api-add-student-group'),
    path('excel/export/', views.ExportExcelReportView.as_view(), name='api-export-excel'),
    path('excel/report-status', views.GetExcelReportView.as_view(), name='api-get-report-excel'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]


urlpatterns += router.urls
