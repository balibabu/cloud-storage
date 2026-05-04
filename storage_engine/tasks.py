import os
from celery import shared_task
from .models import Chunk, UploadStatus
from github_engine.fileHandler import FileHandler

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 1800})
def upload_chunk_to_cloud(self, chunk_id):
    chunk = Chunk.objects.get(id=chunk_id)    
    if chunk.status == UploadStatus.COMPLETED: return 

    chunk.status = UploadStatus.UPLOADING
    chunk.save()
    execution = chunk.execution
    local_path = execution.local_path

    try:
        with open(local_path, 'rb') as f:
            encrypted_data = f.read()

        FileHandler.upload(encrypted_data, str(chunk_id))
        
        chunk.status = UploadStatus.COMPLETED
        if os.path.exists(local_path): os.remove(local_path)
        chunk.save()
        chunk.file.check_and_update_status()

    except Exception as e:
        chunk.status = UploadStatus.FAILED
        chunk.save()
        execution.retry_count += 1
        execution.last_error = str(e)
        execution.save()
        raise e