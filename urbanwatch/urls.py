from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('complaints/', include('complaints.urls')),
    path('users/', include('users.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #to handle media files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) #to handle static files
