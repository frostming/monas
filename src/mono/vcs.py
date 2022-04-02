from __future__ import annotations

from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError


class Git:
    """The git repository wrapper"""

    def __init__(self, path: Path):
        try:
            self.repo = Repo(path)
        except InvalidGitRepositoryError:
            self.repo = Repo.init(path)

    def get_user_name(self) -> str:
        """Get the user's name."""
        return self.repo.config_reader().get_value("user", "name")

    def get_user_email(self) -> str:
        """Get the user's email address."""
        return self.repo.config_reader().get_value("user", "email")

    def get_remote_url(self) -> str | None:
        """Get the remote url."""
        try:
            return self.repo.remote().url
        except ValueError:
            return None
