from __future__ import annotations

import abc
from pathlib import Path
from typing import Any

from monas.questions import InputMetadata


class Metadata(metaclass=abc.ABCMeta):
    """The abstract base class for project metadata"""

    name: str
    filename: str

    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / self.filename

    @abc.abstractclassmethod
    def match(cls, pyproject_data: dict) -> bool:
        """Return True if the project matches the metadata type"""
        pass

    @abc.abstractproperty
    def version(self) -> str:
        """Get the project version"""
        pass

    @version.setter
    def version(self, value: str) -> None:
        """Set the project version"""
        pass

    @abc.abstractclassmethod
    def create(cls, inputs: InputMetadata) -> str:
        """Create the project metadata and return the content"""
        pass

    @abc.abstractmethod
    def add_dependency(self, dependency: str) -> None:
        """Add a dependency to the project"""
        pass

    @abc.abstractmethod
    def remove_dependency(self, dependency: str) -> None:
        """Remove a dependency from the project"""
        pass

    @abc.abstractmethod
    def get_dependency_names(self) -> list[str]:
        """Get a list of canonicalized dependency names"""
        pass

    @abc.abstractmethod
    def get_template_args(self) -> dict[str, Any]:
        """Get a dictionary of (name, description, license, requires_python)"""
        pass
