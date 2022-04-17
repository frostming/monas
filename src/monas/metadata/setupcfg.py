from __future__ import annotations

import configparser
import io
from typing import Any, Iterable

from click import Path
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from monas.metadata.base import Metadata
from monas.questions import InputMetadata


class SetupCfgMetadata(Metadata):
    name = "setupcfg"
    filename = "setup.cfg"

    def __init__(self, root: Path) -> None:
        super().__init__(root)
        self._parser = self._read()

    @classmethod
    def match(cls, pyproject_data: dict) -> bool:
        return (
            pyproject_data.get("build-system", {})
            .get("build-backend", "setuptools.build_metadata")
            .startswith("setuptools")
        )

    def _read(self) -> configparser.ConfigParser:
        parser = configparser.ConfigParser()
        parser.read(self.path)
        return parser

    def _write(self) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            self._parser.write(f)

    @property
    def version(self) -> str:
        return self._parser.get("metadata", "version")

    @version.setter
    def version(self, value: str) -> None:
        self._parser["metadata"]["version"] = value
        self._write()

    @classmethod
    def create(cls, inputs: InputMetadata) -> str:
        metadata = {
            "name": inputs.name,
            "version": inputs.version,
            "description": inputs.description,
            "author": inputs.author,
            "author_email": inputs.author_email,
            "license": inputs.license_expr,
            "long_description": "file: README.md",
            "long_description_content_type": "text/markdown",
        }
        project_urls = {}
        if inputs.homepage:
            project_urls["Home"] = inputs.homepage
        if inputs.remote_repo:
            project_urls["Repository"] = inputs.remote_repo
        if project_urls:
            metadata["project_urls"] = "".join(
                f"\n{key} = {value}" for key, value in project_urls.items()
            )
        options = {
            "packages": "find:",
            "include_package_data": "True",
            "python_requires": inputs.requires_python,
        }
        parser = configparser.ConfigParser()
        parser["metadata"] = metadata
        parser["options"] = options
        fp = io.StringIO()
        parser.write(fp)
        return fp.getvalue()

    def _get_dependencies(self) -> Iterable[str]:
        return filter(
            None,
            (
                dep.strip()
                for dep in self._parser["options"]
                .get("install_requires", "")
                .splitlines()
            ),
        )

    def get_dependency_names(self) -> list[str]:
        return [
            canonicalize_name(Requirement(dependency.strip()).name)
            for dependency in self._get_dependencies()
        ]

    def add_dependency(self, dependency: str) -> None:
        dep_name = canonicalize_name(Requirement(dependency).name)
        dependencies = [
            dep
            for dep in self._get_dependencies()
            if canonicalize_name(Requirement(dep).name) != dep_name
        ]
        dependencies.append(dependency)
        self._parser["options"]["install_requires"] = "".join(
            f"\n{dep}" for dep in dependencies
        )
        self._write()

    def remove_dependency(self, dependency: str) -> None:
        dep_name = canonicalize_name(Requirement(dependency).name)
        dependencies = [
            dep
            for dep in self._get_dependencies()
            if canonicalize_name(Requirement(dep).name) != dep_name
        ]
        self._parser["options"]["install_requires"] = "".join(
            f"\n{dep}" for dep in dependencies
        )
        self._write()

    def get_template_args(self) -> dict[str, Any]:
        return {
            "name": self._parser["metadata"]["name"],
            "description": self._parser["metadata"]["description"],
            "requires_python": self._parser["options"]["python_requires"],
            "license": self._parser["metadata"]["license"],
        }
