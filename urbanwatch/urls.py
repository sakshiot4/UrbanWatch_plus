from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # This will now look inside theme/urls.py correctly
    path('', include('theme.urls')),

    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),
    path('officers/', include('officers.urls')),
    path('contractors/', include('contractors.urls')),
    path('users/', include('users.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)