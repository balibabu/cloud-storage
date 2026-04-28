from django.shortcuts import render
from django.http import HttpResponse
from storage_engine.models import File
from storage_engine.storageHandler import StorageHandler
from django.middleware.csrf import get_token



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


def upload_file(request):
    print('here-1')
    if request.method == "POST":
        raw_file = request.FILES["file"]
        file_id = StorageHandler.upload(raw_file)
        return redirect("index")

    return render(request, "upload.html")


def download_file(request, file_id):
    file_obj = get_object_or_404(File, id=file_id)

    # Example placeholder logic
    chunk_paths = ChunkExecution.objects.filter(
        chunk__file=file_obj
    ).values_list("local_path", flat=True)

    if not chunk_paths:
        raise Http404("File not available")

    # Just return first chunk as demo (replace with real reassembly)
    first_path = chunk_paths[0]

    if not os.path.exists(first_path):
        raise Http404("File missing")

    return FileResponse(open(first_path, "rb"), as_attachment=True, filename=file_obj.title)