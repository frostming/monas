from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Iterable

import click
from rich.console import Console
from rich.theme import Theme

PROJECT_NAME = __name__.split(".")[0]
THEME = Theme(
    {
        "primary": "cyan",
        "info": "grey69",
        "succ": "green bold",
        "notice": "yellow",
        "danger": "red bold",
    }
)

console = Console(theme=THEME)
err_console = Console(theme=THEME, stderr=True)


def info(msg: str) -> None:
    """Print info message."""
    prefix = f"[info]{PROJECT_NAME}[/] "
    err_console.print(prefix + msg, highlight=False)


def run_command(
    cmd: list[str], cwd: str = None, env: dict[str, str] | None = None, **kwargs: Any
) -> subprocess.CompletedProcess:
    """Run command in subprocess"""
    try:
        return subprocess.run(cmd, cwd=cwd, env=env, check=True, **kwargs)
    except subprocess.CalledProcessError:
        err_console.print("[danger]Error running command[/] {}. ")
        raise click.Abort()


def get_preferred_python_version() -> str:
    """Get preferred python version"""
    major, minor = sys.version_info[:2]
    return f"{major}.{minor}"


def ensure_virtualenv(path: Path, python_version: str | None = None) -> None:
    """Ensure virtualenv exists"""
    from virtualenv import cli_run

    if path.exists():
        return
    info(f"Creating virtualenv: [primary]{path}[/]")
    args = [str(path)]
    if python_version:
        args = ["-p", python_version] + args
    cli_run(args, setup_logging=True)


def pip_install(venv_path: Path, requirements: Iterable[str]) -> None:
    """Install the given requirements into the venv"""
    ensure_virtualenv(venv_path)
    if os.name == "nt":
        python = venv_path / "Scripts" / "python.exe"
    else:
        python = venv_path / "bin" / "python"
    with NamedTemporaryFile(
        "w", prefix="monas-", suffix="-reqs.txt", delete=False
    ) as temp:
        for req in requirements:
            temp.write(f"{req}\n")
        temp.close()
        args = [
            str(python),
            "-Im",
            "pip",
            "install",
            "--upgrade",
            "-r",
            temp.name,
        ]
        try:
            run_command(args, cwd=str(venv_path.parent), stdout=subprocess.DEVNULL)
        finally:
            os.unlink(temp.name)


def is_relative_to(path: Path, parent: Path) -> bool:
    """Check if path is relative path to the parent"""
    try:
        path.absolute().relative_to(parent)
        return True
    except ValueError:
        return False


if sys.version_info >= (3, 8):
    from shlex import join as sh_join
else:
    from shlex import quote as quote

    def sh_join(split_command: Iterable[str]) -> str:
        """Return a shell-escaped string from *split_command*."""
        return " ".join(quote(arg) for arg in split_command)
