import os
from dotenv import load_dotenv
from django.conf import settings
from .models import File, Chunk, ChunkExecution
from .tasks import upload_chunk_to_cloud
from .crypto import derive_chunk_key, encrypt_chunk, decrypt_chunk
from github_engine.fileHandler import FileHandler
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse


load_dotenv()
MASTER_KEY = os.getenv('MASTER_KEY').encode("utf-8")
FILE_SIZE_LIMIT = int(os.getenv('FILE_SIZE_LIMIT'))


class StorageHandler:

    def upload(raw_file, chunk_size=FILE_SIZE_LIMIT):
        file_obj = File.objects.create(title=raw_file.name, size=raw_file.size, content_type=raw_file.content_type)
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks')
        os.makedirs(temp_dir, exist_ok=True)
        index = 0
        while True:
            chunk_data = raw_file.read(chunk_size)
            if not chunk_data: break
            key = derive_chunk_key(MASTER_KEY, str(file_obj.id), index)
            encrypted_data = encrypt_chunk(chunk_data, key)
            local_path = os.path.join(temp_dir, f"{index}.enc")
            with open(local_path, 'wb') as f: f.write(encrypted_data)
            chunk = Chunk.objects.create(file=file_obj, index=index)
            ChunkExecution.objects.create(chunk=chunk, local_path=local_path)
            upload_chunk_to_cloud.delay(chunk.id)
            index += 1
        return file_obj.id

    def download(file_uid):
        file = get_object_or_404(File, id=file_uid)
        def file_iterator():
            chunks=file.chunks.all()
            for chunk in chunks:
                key = derive_chunk_key(MASTER_KEY, str(file.id), chunk.index)
                encrypted_data = FileHandler.download(str(chunk.id))
                decrypted_data = decrypt_chunk(encrypted_data, key)
                yield decrypted_data

        response = StreamingHttpResponse(file_iterator(), content_type=file.content_type)
        response['Content-Disposition'] = f'attachment; filename="{file.title}"'
        response['Content-Length'] = file.size
        return response