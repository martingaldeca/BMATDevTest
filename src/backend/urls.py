from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from backend.settings import PRODUCTION

api_url_patterns = [
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='refresh'),
]

urlpatterns = [
    path('api/', include('data_processor.api.urls', 'data_processor')),
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('bmat_admin/', admin.site.urls),

] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
) + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
) + api_url_patterns

if not PRODUCTION:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        path('__debug__/', include('debug_toolbar.urls')),
    ]
