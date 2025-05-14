from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("inventario.urls")),  # Enlazamos las URLs de la nueva app
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)