from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.authentication import SessionAuthentication
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from . import settings

schema_view = get_schema_view(
    openapi.Info(
        title='META - production',
        default_version='v1',
        description="Api",
    ),
    url=settings.SWAGGER_URL,
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(SessionAuthentication,),
)

urlpatterns = [
    # Service
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0)),
    path('rosetta/', include('rosetta.urls')),
    # API
    path('api/user/', include('apps.users.urls')),
    path('api/direction/', include('apps.directions.urls')),
    path('api/group/', include('apps.groups.urls')),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
