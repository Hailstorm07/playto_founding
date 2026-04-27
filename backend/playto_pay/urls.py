from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def health_check(request):
    """Health check endpoint for debugging"""
    return JsonResponse({
        'status': 'ok',
        'debug': settings.DEBUG,
        'host': request.META.get('HTTP_HOST'),
        'allowed_hosts': settings.ALLOWED_HOSTS,
    })

@condition(etag_func=None)
@cache_page(60 * 60)  # Cache for 1 hour
def serve_react_app(request):
    """Serve React app for any non-API route"""
    # Try to serve index.html from staticfiles (where build script copies it)
    possible_paths = [
        os.path.join(settings.BASE_DIR, 'staticfiles', 'index.html'),
        os.path.join(settings.STATIC_ROOT, 'index.html'),
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            try:
                response = FileResponse(open(file_path, 'rb'), content_type='text/html')
                return response
            except Exception as e:
                continue
    
    # If no index.html found, return debug info
    from django.http import HttpResponse
    return HttpResponse(
        f"Frontend not found at any of: {possible_paths}",
        status=404,
        content_type='text/plain'
    )

urlpatterns = [
    path('health/', health_check, name='health'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('kyc.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files with WhiteNoise in production
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Catch-all for React Router - must be last
# Exclude: /api/, /admin/, /health/, /static/, /assets/, /media/
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^(?!api)(?!admin)(?!health)(?!static)(?!assets)(?!media).*?/?$', serve_react_app, name='react_app'),
    ]
