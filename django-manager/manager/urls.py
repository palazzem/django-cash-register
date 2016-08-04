from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('registers.urls')),
    url(r'^pos/', include('pos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
