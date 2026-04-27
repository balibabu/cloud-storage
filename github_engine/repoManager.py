import time, uuid
from .models import Repo
from .githubManager import GithubManager

class RepoManager:

    def _get_repos():
        return list(Repo.get_repos())

    def _get_size(repo):
        return Repo.get_size(repo)

    def add_size(repo, size):
        repo_obj, created = Repo.objects.get_or_create(name=repo)
        repo_obj.size += size
        repo_obj.save()
        
    def get_free_repo(file_size, repo_size_limit, token):
        repos = RepoManager._get_repos()
        for repo in repos:
            if RepoManager._get_size(repo)+file_size<= repo_size_limit:
                return repo

        rname = str(uuid.uuid4())
        git=GithubManager(token)
        git.create_repo(rname)
        RepoManager.add_size(rname, 0)
        return rname
    