import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")  

def create_pull_request(branch_name: str, title: str, description: str) -> str:
    """
    Creates a pull request on the target repository.
    """
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(GITHUB_REPO)
        base_branch = repo.default_branch

        pr = repo.create_pull(
            title=title,
            body=description,
            head=branch_name,
            base=base_branch
        )
        return f"Pull Request created: {pr.html_url}"
    except Exception as e:
        return f"Failed to create PR: {e}"
