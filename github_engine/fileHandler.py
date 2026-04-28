from .repoManager import RepoManager
from .githubManager import GithubManager
from .models import GitFile
from dotenv import load_dotenv
import os
load_dotenv()

REPO_SIZE_LIMIT =  int(os.getenv('REPO_SIZE_LIMIT'))
TOKEN = os.getenv('TOKEN')

class FileHandler:

    def upload(file_content: bytes, file_uid: str):
        size = len(file_content)
        rname = RepoManager.get_free_repo(size, REPO_SIZE_LIMIT, TOKEN)
        gm = GithubManager(TOKEN)
        gm.upload_file(file_content, file_uid, rname)
        gm.close_connection()
        RepoManager.add_size(rname, size)
        GitFile.objects.create(repo=rname,filename=file_uid)

    def download(file_uid):
        file=GitFile.objects.get(filename=file_uid)
        gm = GithubManager(TOKEN)
        file_content = gm.download_file(file_uid, file.repo)
        return file_content