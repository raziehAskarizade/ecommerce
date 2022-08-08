from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user.urls')),
    path('order/', include('order.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('docs/', include_docs_urls(title='Shopping test')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
