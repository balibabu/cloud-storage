# tasks.py
import os
from celery import shared_task
from .models import Chunk, UploadStatus

# autoretry_for catches network errors, retry_kwargs tells it to wait 5 mins (300 secs)
@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 300})
def upload_chunk_to_cloud(self, chunk_id):
    chunk = Chunk.objects.get(id=chunk_id)
    
    if chunk.status == UploadStatus.COMPLETED: return # Already done!

    chunk.status = UploadStatus.UPLOADING
    chunk.save()

    try:
        # 1. Read encrypted data from local disk
        with open(chunk.local_path, 'rb') as f:
            encrypted_data = f.read()

        # 2. UPLOAD TO CLOUD API (Mocked here)
        # cloud_response = my_cloud_service.upload(
        #     data=encrypted_data, 
        #     folder=chunk.folder,
        #     filename=f"{chunk.index}.enc"
        # )
        
        # 3. Update the database on success
        chunk.status = UploadStatus.COMPLETED
        if os.path.exists(chunk.local_path): os.remove(chunk.local_path)
        chunk.local_path = None
        chunk.save()
        chunk.file.check_and_update_status() # Check if the whole file is done

    except Exception as e:
        # If the upload fails, mark it failed and raise exception to trigger Celery's auto-retry
        chunk.status = UploadStatus.FAILED
        chunk.save()
        raise e # Celery catches this and waits given minutes before trying again!