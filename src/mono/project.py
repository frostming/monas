from __future__ import annotations

import textwrap
from dataclasses import dataclass
from pathlib import Path

import tomlkit
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from tomlkit.toml_file import TOMLFile

from mono.config import Config
from mono.utils import pip_install

BUILD_BACKENDS = {
    "setuptools": {
        "requires": ["setuptools>=61", "wheel"],
        "build-backend": "setuptools.build_meta",
    },
    "pdm": {"requires": ["pdm-pep517"], "build-backend": "pdm.pep517.api"},
    "flit": {"requires": ["flit_core>=3.2,<4"], "build-backend": "flit_core.buildapi"},
    "hatch": {"requires": ["hatchling>=0.22.0"], "build-backend": "hatchling.build"},
}

FILE_TEMPLATES = {
    "README.md": textwrap.dedent(
        """\
        # {name}

        ## Requirement

        Python {requires_python}

        ## Installation

        ```bash
        pip install {name}
        ```

        ## License

        {license}
        """
    )
}

SETUP_TEMPLATE = """\
from setuptools import setup

setup(name={name!r})
"""


@dataclass(frozen=True)
class InputMetadata:
    """Package metadata class"""

    name: str
    version: str
    description: str
    license_expr: str
    author: str
    remote_repo: str
    author_email: str
    homepage: str
    requires_python: str
    build_backend: str


class PyPackage:
    """A Python project managed by Mono"""

    def __init__(self, config: Config, path: Path) -> None:
        self.config = config
        self.path = path.absolute()
        self.toml_path = self.path / "pyproject.toml"
        self.toml_file = TOMLFile(self.toml_path)

    @property
    def canonical_name(self) -> str:
        """Get the project name"""
        return canonicalize_name(self.path.name)

    @property
    def version(self) -> str:
        """Get the project version"""
        return self.toml_file.read()["project"]["version"]

    def build_toml(self, metadata: InputMetadata) -> tomlkit.TOMLDocument:
        """Create a new package"""
        license_table = tomlkit.inline_table()
        license_table.update({"text": metadata.license_expr})
        authors = tomlkit.array()
        author_table = tomlkit.inline_table()
        author_table.update({"name": metadata.author, "email": metadata.author_email})
        authors.append(author_table)

        pep621_data = {
            "name": metadata.name,
            "version": metadata.version,
            "description": metadata.description,
            "authors": authors,
            "license": license_table,
            "requires-python": metadata.requires_python,
            "readme": "README.md",
            "dependencies": [],
        }
        project_urls = {}
        if metadata.homepage:
            project_urls["Home"] = metadata.homepage
        if metadata.remote_repo:
            project_urls["Repository"] = metadata.remote_repo
        if project_urls:
            pep621_data["urls"] = project_urls
        build_system = BUILD_BACKENDS[metadata.build_backend]
        doc = tomlkit.document()
        doc.update({"project": pep621_data, "build-system": build_system})
        return doc

    def write_toml(self, doc: tomlkit.TOMLDocument) -> None:
        """Write the pyproject.toml file"""
        if not self.path.exists():
            self.path.mkdir(parents=True)
        self.toml_file.write(doc)

    def create_project_files(self) -> None:
        """Create the project files"""
        metadata = self.toml_file.read()
        template_args = {
            "name": metadata["project"]["name"],
            "requires_python": metadata["project"]["requires-python"],
            "license": metadata["project"].get("license-expression")
            or metadata["project"]["license"].get("text", ""),
        }
        for filename, template in FILE_TEMPLATES.items():
            with open(self.path / filename, "w", encoding="utf-8") as f:
                f.write(template.format(**template_args))
        if metadata["build-system"]["build-backend"] == "setuptools.build_meta":
            with open(self.path / "setup.py", "w", encoding="utf-8") as f:
                f.write(SETUP_TEMPLATE.format(**template_args))

        package_dir = self.path.joinpath(self.canonical_name.replace("-", "_"))
        package_dir.mkdir()
        package_dir.joinpath("__init__.py").touch()

    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the project"""
        metadata = self.toml_file.read()
        dep_name = canonicalize_name(Requirement(dependency).name)
        dependencies = [
            dep
            for dep in metadata["project"].get("dependencies", [])
            if canonicalize_name(Requirement(dep).name) != dep_name
        ]
        dependencies.append(dependency)
        metadata["project"]["dependencies"] = tomlkit.item(dependencies).multiline(True)
        self.write_toml(metadata)

    def install(self) -> None:
        """Bootstrap the package and link depending packages in the monorepo"""
        dependency_names = [
            canonicalize_name(Requirement(dep).name)
            for dep in self.toml_file.read()["project"].get("dependencies", [])
        ]
        packages = [
            pkg
            for pkg in self.config.iter_packages()
            if pkg.canonical_name in dependency_names
        ] + [self]
        requirements = [f"-e {pkg.path.as_posix()}" for pkg in packages]
        pip_install(self.path / ".venv", requirements)
