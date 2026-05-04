import uuid
from django.db import models

class UploadStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    UPLOADING = 'UPLOADING', 'Uploading'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'


class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    size = models.PositiveBigIntegerField()
    content_type = models.CharField(max_length=128, default='application/octet-stream')
    status = models.CharField(max_length=20, choices=UploadStatus.choices, default=UploadStatus.PENDING)
    def __str__(self): return self.title

    def check_and_update_status(self):
        """Helper to mark the whole file as completed if all chunks are uploaded."""
        if not self.chunks.exclude(status=UploadStatus.COMPLETED).exists():
            self.status = UploadStatus.COMPLETED
            self.save()


class Chunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="chunks")
    index = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=UploadStatus.choices, default=UploadStatus.PENDING)
    def __str__(self): return f"{self.file.title}-C[{self.index}]-({self.status})"

    class Meta: 
        unique_together = ('file', 'index')
        ordering = ['index']


class ChunkExecution(models.Model):
    chunk = models.OneToOneField(Chunk, on_delete=models.CASCADE, related_name="execution")
    local_path = models.CharField(max_length=500, null=True, blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    def __str__(self): return f"{self.chunk.file.title}-C[{self.chunk.index}] (retry:{self.retry_count})"
