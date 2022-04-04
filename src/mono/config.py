from __future__ import annotations

import sys
import typing
from pathlib import Path
from typing import Iterable

import click
from tomlkit.toml_file import TOMLFile

from mono.vcs import Git

if typing.TYPE_CHECKING:
    from tomlkit.toml_document import TOMLDocument
    from mono.project import PyPackage


class Config:
    """The configuration for mono tool.

    It is stored as [tool.mono] table in the `pyproject.toml` file.
    """

    _pyproject: TOMLDocument
    _tool: dict

    def __init__(self) -> None:
        self.path = self._locate_mono_project()

    def _locate_mono_project(self) -> Path:
        """Find the pyproject.toml with mono setting in the current or parent dirs"""
        path = Path.cwd().absolute()
        for parent in [path, *path.parents]:
            if not (parent / "pyproject.toml").exists():
                continue
            self._pyproject = TOMLFile(parent / "pyproject.toml").read()
            self._tool = self._pyproject.setdefault("tool", {}).setdefault("mono", {})
            if self._tool:
                return parent
        raise click.UsageError("Mono repo isn't initialized, have you run `mono init`?")

    def get_repo(self) -> Git:
        """Get the git repository."""
        return Git(self.path.parent)

    @property
    def root_venv(self) -> Path:
        return self.path / ".venv"

    @property
    def homepage(self) -> str | None:
        """Get the homepage."""
        urls = self._pyproject.get("project", {}).get("urls", {})
        return urls.get("Home", urls.get("Homepage"))

    @property
    def package_paths(self) -> list[Path]:
        """The list of paths that contain packages"""
        return [self.path / p for p in self._tool.get("packages", [])]

    @property
    def version(self) -> str:
        """The version of the monorepo"""
        return self._tool.get("version", "0.0.0")

    @property
    def python_version(self) -> str:
        """The selected Python version"""
        return self._tool.get(
            "python-version", ".".join(map(str, sys.version_info[:2]))
        )

    def add_package_path(self, path: str) -> None:
        """Add a package path to the configuration"""
        self._tool.setdefault("packages", []).append(path)

    def iter_packages(self) -> Iterable[PyPackage]:
        """Iterate over the packages in the monorepo"""
        from mono.project import PyPackage

        for p in self.package_paths:
            for package in p.iterdir():
                if package.is_dir():
                    yield PyPackage(self, package)


pass_config = click.make_pass_decorator(Config, ensure=True)
