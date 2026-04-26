from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import FileResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.http import condition
import os

@condition(etag_func=None)
@cache_page(60 * 60)  # Cache for 1 hour
def serve_react_app(request):
    """Serve React app for any non-API route"""
    # Try to serve index.html from dist folder
    possible_paths = [
        os.path.join(settings.STATIC_ROOT, 'dist', 'index.html'),
        os.path.join(settings.BASE_DIR, 'staticfiles', 'dist', 'index.html'),
    ]
    
    for file_path in possible_paths:
        if os.path.exists(file_path):
            try:
                response = FileResponse(open(file_path, 'rb'), content_type='text/html')
                return response
            except Exception:
                continue
    
    # If no index.html found, return 404
    from django.http import HttpResponse
    return HttpResponse("Frontend not built. Please run the build command.", status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('kyc.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve React frontend in production - catch all non-API routes
    urlpatterns += [
        re_path(r'^(?!api)(?!admin)(?!static).*?/?$', serve_react_app, name='react_app'),
    ]
