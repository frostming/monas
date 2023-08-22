from __future__ import annotations

import textwrap
from pathlib import Path
from shlex import join as sh_join
from typing import Optional, Type, cast

import tomlkit
from packaging.utils import canonicalize_name
from tomlkit.toml_file import TOMLFile

from monas.config import Config
from monas.metadata import ALL_METADATA_CLASSES, Metadata
from monas.questions import InputMetadata
from monas.utils import pip_install

BUILD_BACKENDS = {
    "setuptools": {
        "requires": ["setuptools>=61", "wheel"],
        "build-backend": "setuptools.build_meta",
    },
    "pdm": {"requires": ["pdm-backend"], "build-backend": "pdm.backend"},
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


def get_metadata_class_for_backend(name: str) -> type[Metadata]:
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
    def name(self) -> str:
        """Get the project name"""
        return self.metadata.package_name

    @property
    def canonical_name(self) -> str:
        """Get the project name"""
        return canonicalize_name(self.name)

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
        local_dependencies = self.get_local_dependencies([self])
        requirements = [
            sh_join(["-e", pkg.path.as_posix()]) for pkg in local_dependencies
        ]
        pip_install(self.path / ".venv", requirements)

    def get_local_dependencies(
        self,
        local_dependencies: list[PyPackage] | None = None,
    ) -> list[PyPackage]:
        """Return list of local dependencies.

        Args:
            local_dependencies: Accumulated list of local depencies to install
        """
        if not local_dependencies:
            local_dependencies = []
        dependency_names = self.metadata.get_dependency_names()
        local_packages = list(self.config.iter_packages())
        for pkg in local_packages:
            pkg_name = pkg.canonical_name
            if pkg_name not in dependency_names:
                continue
            if pkg_name == self.canonical_name:
                raise ValueError(f'{self.name} cannot have a dependency on itself')
            if pkg_name in [ld.canonical_name for ld in local_dependencies]:
                continue
            local_dependencies = [pkg, *local_dependencies]
            local_dependencies = pkg.get_local_dependencies(local_dependencies)
        return local_dependencies
