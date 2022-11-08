from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


app_name = 'apps.directions'


router = DefaultRouter()
router.register(r'direction', views.DirectionViewSet, basename='direction')
router.register(r'subject', views.SubjectViewSet, basename='subject')


urlpatterns = [
    path('add-curator/', views.AddCuratorInDirectionView.as_view(), name='api-add-curator'),
]


urlpatterns += router.urls
