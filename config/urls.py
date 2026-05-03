from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('file/', include('filespace.urls')),
    path('storage/', include('storage.urls')),
    re_path(r'^.*$', include('common.urls'))
]
