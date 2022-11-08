from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'apps.groups'


router = DefaultRouter()
router.register(r'groups', views.StudentGroupViewSet, basename='group')

urlpatterns = [
    path('list/', views.StudentGroupListSerializer.as_view(), name='groups'),
]

urlpatterns += router.urls
