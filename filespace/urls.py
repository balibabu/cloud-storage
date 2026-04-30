from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'filespace'

urlpatterns =[
    path('', views.index, name='index'),
    path('folder/<int:folder_id>/', views.index, name='folder'),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('upload/', views.upload_file, name='upload_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
]