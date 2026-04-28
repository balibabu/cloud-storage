from github import Github, Auth
import base64

class GithubManager:
    def __init__(self, token) -> None:
        auth = Auth.Token(token)
        self.git=Github(auth=auth)

    def upload_file(self, fileContent, filename, repo_name):
        user=self.git.get_user()
        repo = user.get_repo(repo_name)
        repo.create_file(path=filename, message='uploaded '+filename, content=fileContent)

    def download_file(self,filename,repo_name):
        user=self.git.get_user()
        repo = user.get_repo(repo_name)
        file = repo.get_contents(filename)
        blob_content = repo.get_git_blob(file.sha).content
        content_bytes = base64.b64decode(blob_content)
        return content_bytes

    def create_repo(self,repo_name):
        user=self.git.get_user()
        user.create_repo(repo_name,private=True)

    def close_connection(self):
        self.git.close()