from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Type, cast

import tomlkit
from packaging.utils import canonicalize_name
from tomlkit.toml_file import TOMLFile

from monas.config import Config
from monas.metadata import ALL_METADATA_CLASSES, Metadata
from monas.questions import InputMetadata
from monas.utils import pip_install, sh_join

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

        {description}

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


def get_build_system_for_backend(name: str) -> dict:
    name = name.split("(")[0]
    return BUILD_BACKENDS[name]


def get_metadata_class_for_backend(name: str) -> Type[Metadata]:
    backend, _, extra = name.partition("(")
    if backend == "setuptools":
        class_name = "pep621" if extra.rstrip(")") == "pyproject.toml" else "setupcfg"
    else:
        class_name = "pep621"
    result = next((cls for cls in ALL_METADATA_CLASSES if cls.name == class_name), None)
    if result is None:
        raise ValueError(f"Unsupported backend {name}")
    return cast(Type[Metadata], result)


class PyPackage:
    """A Python project managed by Monas"""

    def __init__(self, config: Config, path: Path) -> None:
        self.config = config
        self.path = path
        self.metadata = self._get_metadata()

    def _get_metadata(self) -> Metadata:
        try:
            pyproject_data = TOMLFile(self.path / "pyproject.toml").read()
        except FileNotFoundError:
            pyproject_data = {}
        result = next(
            (cls for cls in ALL_METADATA_CLASSES if cls.match(pyproject_data)), None
        )
        if result is None:
            raise ValueError("Can't determine a metadata type from the pyproject.toml")
        return cast(Type[Metadata], result)(self.path)

    @property
    def canonical_name(self) -> str:
        """Get the project name"""
        return canonicalize_name(self.path.name)

    @property
    def version(self) -> str:
        """Get the project version"""
        return self.metadata.version

    def set_version(self, version: str) -> None:
        """Set the project version"""
        self.metadata.version = version

    @classmethod
    def create(cls, config: Config, path: Path, inputs: InputMetadata) -> None:
        """Create a python package at the given path"""
        metadata = get_metadata_class_for_backend(inputs.build_backend)(path)
        template_args = metadata.get_template_args()
        for filename, template in FILE_TEMPLATES.items():
            with open(path / filename, "w", encoding="utf-8") as f:
                f.write(template.format(**template_args))

        pyproject_toml = TOMLFile(path / "pyproject.toml")
        try:
            data = pyproject_toml.read()
        except FileNotFoundError:
            data = tomlkit.document()
        data.append("build-system", get_build_system_for_backend(inputs.build_backend))
        pyproject_toml.write(data)

        if inputs.build_backend.startswith("setuptools"):
            with open(path / "setup.py", "w", encoding="utf-8") as f:
                f.write(SETUP_TEMPLATE.format(**template_args))

        package_dir = path / canonicalize_name(path.name).replace("-", "_")
        package_dir.mkdir()
        package_dir.joinpath("__init__.py").touch()
        return cls(config, path)

    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the project.

        Args:
            dependency: A requirement string(PEP 508)
        """
        self.metadata.add_dependency(dependency)

    def remove_dependency(self, dependency: str) -> None:
        """Remove a dependency from the project.

        Args:
            dependency: A canonicalized requirement name
        """
        self.metadata.remove_dependency(dependency)

    def install(self) -> None:
        """Bootstrap the package and link depending packages in the monorepo"""
        dependency_names = self.metadata.get_dependency_names()
        packages = [
            pkg
            for pkg in self.config.iter_packages()
            if pkg.canonical_name in dependency_names
        ] + [self]
        requirements = [sh_join(["-e", pkg.path.as_posix()]) for pkg in packages]
        pip_install(self.path / ".venv", requirements)
