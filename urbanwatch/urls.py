from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Homepage Route
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    #Allauth login/signup/logout.
    path('accounts/', include('allauth.urls')),
    #Custom contractor signup.
    path('accounts/', include('accounts.urls')),
    path('complaints/', include('complaints.urls')),
    path('officers/', include('officers.urls')),
    path('contractors/', include('contractors.urls')),
    path('users/', include('users.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #to handle media files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) #to handle static files
