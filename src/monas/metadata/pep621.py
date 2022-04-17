from __future__ import annotations

from typing import Any

import tomlkit
from click import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from tomlkit.toml_file import TOMLFile

from monas.metadata.base import Metadata
from monas.questions import InputMetadata


class PEP621Metadata(Metadata):
    name = "pep621"
    filename = "pyproject.toml"

    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self._data = self._read()

    @classmethod
    def match(cls, pyproject_data: dict) -> bool:
        return bool(pyproject_data.get("project", {}).get("name"))

    def _read(self) -> tomlkit.TOMLDocument:
        return TOMLFile(self.path).read()

    def _write(self) -> None:
        TOMLFile(self.path).write(self._data)

    @property
    def version(self) -> str:
        return self._data["project"]["version"]

    @version.setter
    def version(self, value: str) -> None:
        self._data["project"]["version"] = value
        self._write()

    @classmethod
    def create(cls, inputs: InputMetadata) -> str:
        license_table = tomlkit.inline_table()
        license_table.update({"text": inputs.license_expr})
        authors = tomlkit.array()
        author_table = tomlkit.inline_table()
        author_table.update({"name": inputs.author, "email": inputs.author_email})
        authors.append(author_table)

        pep621_data = {
            "name": inputs.name,
            "version": inputs.version,
            "description": inputs.description,
            "authors": authors,
            "license": license_table,
            "requires-python": inputs.requires_python,
            "readme": "README.md",
            "dependencies": [],
        }
        project_urls = {}
        if inputs.homepage:
            project_urls["Home"] = inputs.homepage
        if inputs.remote_repo:
            project_urls["Repository"] = inputs.remote_repo
        if project_urls:
            pep621_data["urls"] = project_urls
        doc = tomlkit.document()
        doc.append("project", pep621_data)
        return tomlkit.dumps(doc)

    def get_dependency_names(self) -> list[str]:
        return [
            canonicalize_name(Requirement(dependency).name)
            for dependency in self._data["project"].get("dependencies", [])
        ]

    def add_dependency(self, dependency: str) -> None:
        dep_name = canonicalize_name(Requirement(dependency).name)
        dependencies = [
            dep
            for dep in self._data["project"].get("dependencies", [])
            if canonicalize_name(Requirement(dep).name) != dep_name
        ]
        dependencies.append(dependency)
        array = tomlkit.array().multiline(True)
        array.extend(dependencies)
        self._data["project"]["dependencies"] = array
        self._write()

    def remove_dependency(self, dependency: str) -> None:
        dep_name = canonicalize_name(Requirement(dependency).name)
        dependencies = [
            dep
            for dep in self._data["project"].get("dependencies", [])
            if canonicalize_name(Requirement(dep).name) != dep_name
        ]
        array = tomlkit.array().multiline(True)
        array.extend(dependencies)
        self._data["project"]["dependencies"] = array
        self._write()

    def get_template_args(self) -> dict[str, Any]:
        return {
            "name": self._data["project"]["name"],
            "description": self._data["project"]["description"],
            "requires_python": self._data["project"]["requires-python"],
            "license": self._data["project"]["license"]["text"],
        }
