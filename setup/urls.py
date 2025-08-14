from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    # path('payments/', include('payments.urls_beta')),
    path('payments/', include('payments.urls')),
    path('api/', include('api.urls')),

    # URLs para o Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # UI:
    # interface interativa do Swagger
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # documentação alternativa, mais limpa e minimalista
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),


    path('', include('crm.urls')),
    # path('cms/', include('cms.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
