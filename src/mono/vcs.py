from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import git
from git import Repo
from git.exc import InvalidGitRepositoryError


class DescribeResult(NamedTuple):
    tag: str
    distance: int
    commit: str
    is_dirty: bool


def _parse_describe_result(result: str) -> DescribeResult:
    if "-" not in result:
        return DescribeResult("", 0, result, False)
    if result.endswith("-dirty"):
        is_dirty = True
        result = result[:-6]
    else:
        is_dirty = False
    tag, distance, node = result.rsplit("-", 2)
    return DescribeResult(tag, int(distance), node.lstrip("g"), is_dirty)


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

    def describe_ref(self) -> DescribeResult:
        """Get the describe tag."""
        try:
            output = self.repo.git.describe("--dirty", "--long", "--tags", "--always")
        except git.GitCommandError:
            output = ""
        return _parse_describe_result(output)

    def diff(self, ref: str) -> list[str]:
        """Get the diff between the current commit and the given ref."""
        return [
            f.strip()
            for f in self.repo.git.diff("--name-only", ref).splitlines()
            if f.strip()
        ]

    def commit(self, message: str) -> None:
        """Commit the changes."""
        self.repo.git.add(".")
        self.repo.git.commit(m=message)

    def tag(self, tag: str, message: str) -> None:
        self.repo.git.tag(tag, a=True, m=message)

    def push(self, including_tags: bool = True) -> None:
        self.repo.git.push()
        if including_tags:
            self.repo.git.push("--tags")
