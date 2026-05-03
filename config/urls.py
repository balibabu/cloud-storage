from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('files/', include('filespace.urls')),
    re_path(r'^.*$', include('common.urls'))
]
