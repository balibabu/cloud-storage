import os
from django.conf import settings
from .models import File, Chunk
from .tasks import upload_chunk_to_cloud # We will define this next

def handle_incoming_file(raw_file):
    # 1. Create the File record
    file_obj = File.objects.create(
        title=raw_file.name,
        size=raw_file.size,
        content_type=raw_file.content_type
    )

    # 2. Setup local temp directory
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks', str(file_obj.id))
    os.makedirs(temp_dir, exist_ok=True)

    index = 0
    chunk_size = 1024 * 1024 * 5 # 5MB
    
    while True:
        chunk_data = raw_file.read(chunk_size)
        if not chunk_data:
            break
        
        # (Assuming you use the derive_chunk_key and encrypt_chunk functions here)
        key = derive_chunk_key(MASTER_KEY, str(file_obj.id), index)
        encrypted_data = encrypt_chunk(chunk_data, key)
        
        # 3. Save locally
        local_path = os.path.join(temp_dir, f"{index}.enc")
        with open(local_path, 'wb') as f:
            f.write(encrypted_data)
        
        # 4. Create the Chunk record with the 'folder' logic you wanted
        chunk = Chunk.objects.create(
            file=file_obj,
            index=index,
            local_path=local_path
        )
        
        # 5. TRIGGER BACKGROUND TASK
        upload_chunk_to_cloud.delay(chunk.id)
        
        index += 1

    return file_obj.id