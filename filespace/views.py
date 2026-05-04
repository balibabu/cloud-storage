from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Folder, UserFile
from storage_engine.models import File
from storage_engine.storageHandler import StorageHandler


@login_required
def index(request, folder_id=None):
    current_folder = None
    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    
    folders = Folder.objects.filter(user=request.user, parent=current_folder)
    files = UserFile.objects.filter(user=request.user, folder=current_folder)

    # Breadcrumbs generation
    breadcrumbs =[]
    f = current_folder
    while f:
        breadcrumbs.insert(0, f)
        f = f.parent

    context = {
        'current_folder': current_folder,
        'folders': folders,
        'files': files,
        'breadcrumbs': breadcrumbs,
        'total_size': sum([file.file.size for file in files])
    }
    return render(request, 'filespace/index.html', context)

@login_required
def create_folder(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_id')
        
        parent_folder = None
        if parent_id:
            parent_folder = get_object_or_404(Folder, id=parent_id, user=request.user)
            
        if name:
            Folder.objects.get_or_create(user=request.user, name=name, parent=parent_folder)
            
        if parent_id:
            return redirect('filespace:folder', folder_id=parent_id)
        return redirect('filespace:index')

@login_required
def upload_file(request):
    if request.method == 'POST':
        raw_file = request.FILES.get('file')
        folder_id = request.POST.get('folder_id')

        if not raw_file:
            return HttpResponseBadRequest("No file uploaded")

        parent_folder = None
        if folder_id:
            parent_folder = get_object_or_404(Folder, id=folder_id, user=request.user)

        # Call your handler
        file_uid = StorageHandler.upload(raw_file)

        # Retrieve the File created by StorageHandler
        core_file = get_object_or_404(File, id=file_uid)

        # Link it to the user's space
        UserFile.objects.create(
            user=request.user,
            folder=parent_folder,
            file=core_file
        )

        return JsonResponse({'message': 'Upload complete', 'status': core_file.status})
    return HttpResponseBadRequest("Invalid request")

@login_required
def download_file(request, file_id):
    user_file = get_object_or_404(UserFile, id=file_id, user=request.user)
    
    # Returns the StreamingHttpResponse from your handler
    response = StorageHandler.download(user_file.file.id) 
    return response