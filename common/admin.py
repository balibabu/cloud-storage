from django.contrib import admin

from storage_engine.models import File, Chunk, ChunkExecution
admin.site.register(File)
admin.site.register(Chunk)
admin.site.register(ChunkExecution)

from github_engine.models import Repo, GitFile
admin.site.register(Repo)
admin.site.register(GitFile)

from filespace.models import Folder, UserFile
admin.site.register(Folder)
admin.site.register(UserFile)