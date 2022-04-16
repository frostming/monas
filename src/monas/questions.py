from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import questionary


@dataclass
class Question:
    """Question class"""

    description: str
    default: str | Callable[[dict[str, str]], str] | None = None
    choices: list[str] | None = None
    instruction: str | None = None

    def get_default(
        self, func: Callable[[dict[str, str]], str]
    ) -> Callable[[dict[str, str]], str]:
        """A decoractor to set the default function.

        Args:
            func: A function that takes the previous answers as the first argument and
                returns the default value.
        """
        self.default = func
        return func

    def ask(self, answers: dict[str, str], default: str | None = None) -> str:
        """Prompt user for the answer.

        Args:
            answers: The answers that have been given before.
        """
        if default is None:
            if callable(self.default):
                default = self.default(answers)
            else:
                default = self.default
        if not self.choices:
            return questionary.text(self.description, default=default).ask()
        return questionary.select(
            self.description, choices=self.choices, default=default, pointer="▶"
        ).ask()


package_questions = {
    "name": Question("package name:"),
    "version": Question("version:", default="0.0.0"),
    "description": Question("description:", default=""),
    "license_expr": Question("license:", default="MIT", instruction="SPDX identifier"),
    "author": Question("author", ""),
    "author_email": Question("author email:", ""),
    "homepage": Question("homepage:", ""),
    "requires_python": Question("requires_python:", default=">=3.7"),
    "build_backend": Question(
        "Build backend:",
        choices=[
            "setuptools(setup.cfg)",
            "setuptools(pyprojec.toml)",
            "pdm",
            "flit",
            "hatch",
        ],
        default="setuptools(setup.cfg)",
    ),
}


def ask_for(questions: dict[str, Question], **kwargs: str) -> dict[str, str]:
    """Ask questions and return answers.

    Args:
        questions: The questions to ask.
        **kwargs: The answers that have been given before.
    """
    answers = {}
    for key, question in questions.items():
        answers[key] = question.ask(answers, kwargs.get(key))
    return answers


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
