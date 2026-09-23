from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


class ForceCorsMiddleware:
    """Force CORS headers on every response, no matter what."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response


urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/', include('jobs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)