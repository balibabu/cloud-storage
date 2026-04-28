from rest_framework.decorators import api_view
from django.shortcuts import redirect
from django.http import HttpResponse
from storage_engine.storageHandler import StorageHandler
from django.middleware.csrf import get_token



@api_view(['GET'])
def index(request):
    csrf_token = get_token(request)
    return HttpResponse(f"""
        <h2>Upload File</h2>
        <form action="upload/" method="post" enctype="multipart/form-data">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <input type="file" name="file" required>
            <button type="submit">Upload</button>
        </form>
    """)


@api_view(['POST'])
def upload_file(request):
    raw_file = request.FILES["file"]
    file_id = StorageHandler.upload(raw_file)
    return redirect("index")


@api_view(['GET'])
def download_file(request, file_id):
    return StorageHandler.download(file_id)