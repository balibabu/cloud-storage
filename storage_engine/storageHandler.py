import os
from dotenv import load_dotenv
from django.conf import settings
from .models import File, Chunk
from .tasks import upload_chunk_to_cloud # We will define this next
from .crypto import derive_chunk_key, encrypt_chunk, decrypt_chunk
from github_engine.fileHandler import FileHandler

load_dotenv()
MASTER_KEY = os.getenv('MASTER_KEY')


class StorageHandler:

    def upload(raw_file):
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
            
            # 4. Create the Chunk record 
            chunk = Chunk.objects.create(
                file=file_obj,
                index=index,
                local_path=local_path
            )
            
            # 5. TRIGGER BACKGROUND TASK
            upload_chunk_to_cloud.delay(chunk.id)
            
            index += 1

        return file_obj.id

    def download(file_uid):
        file = get_object_or_404(File, id=file_uid)

        def file_iterator():
            chunks=file.chunks.all()
            for chunk in chunks:
                key = derive_chunk_key(MASTER_KEY, str(file.id), chunk.index)
                encrypted_data = FileHandler.download(chunk.id, chunk.folder)
                decrypted_data = decrypt_chunk(encrypted_data, key)
                yield decrypted_data

        response = StreamingHttpResponse(file_iterator(), content_type=file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.title}"'
        response['Content-Length'] = file.size
        return response