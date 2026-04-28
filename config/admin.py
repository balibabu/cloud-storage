from django.contrib import admin

from storage_engine.models import File, Chunk, ChunkExecution
admin.site.register(File)
admin.site.register(Chunk)
admin.site.register(ChunkExecution)