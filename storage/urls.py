from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload_file, name="upload"),
    path("download/<uuid:file_id>/", views.download_file, name="download"),
]