from django.db import models

class Repo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    size = models.PositiveBigIntegerField(default=0)
    def __str__(self): return f'{self.name} [{self.size}]'

    def add_size(self, size):
        self.size += size
        self.save()

    @classmethod
    def get_size(cls, rname):
        try:
            repo = cls.objects.get(name=rname)
            return repo.size
        except cls.DoesNotExist:
            return 0
            
    @classmethod
    def get_repos(cls):
        return cls.objects.all().values_list('name', flat=True)


class GitFile(models.Model):
    filename = models.CharField(max_length=255, unique=True)
    repo = models.CharField(max_length=255)
    def __str__(self): return f'{self.filename} (Repo-{self.repo.split('-')[0]})'
