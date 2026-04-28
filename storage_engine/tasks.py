import os
from celery import shared_task
from .models import Chunk, UploadStatus
from github_engine.fileHandler import FileHandler

# autoretry_for catches network errors, retry_kwargs tells it to wait 5 mins (300 secs)
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 300})
def upload_chunk_to_cloud(self, chunk_id):
    print('here-3')
    chunk = Chunk.objects.get(id=chunk_id)    

    
    if chunk.status == UploadStatus.COMPLETED: return # Already done!

    chunk.status = UploadStatus.UPLOADING
    chunk.save()
    execution = chunk.execution
    local_path = execution.local_path

    try:
        # 1. Read encrypted data from local disk
        with open(local_path, 'rb') as f:
            encrypted_data = f.read()

        # 2. UPLOAD TO CLOUD
        FileHandler.upload(encrypted_data, str(chunk_id))
        print('here-4')
        
        # 3. Update the database on success
        chunk.status = UploadStatus.COMPLETED
        if os.path.exists(local_path): os.remove(local_path)
        chunk.save()
        chunk.file.check_and_update_status() # Check if the whole file is done

    except Exception as e:
        # If the upload fails, mark it failed and raise exception to trigger Celery's auto-retry
        chunk.status = UploadStatus.FAILED
        chunk.save()
        execution.retry_count += 1
        execution.last_error = str(e)
        execution.save()
        raise e # Celery catches this and waits given minutes before trying again!