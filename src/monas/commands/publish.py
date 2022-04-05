from __future__ import annotations

import functools
import os
import shutil
import sys
from asyncio import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import rich_click as click
from click.decorators import pass_context
from rich.prompt import Confirm

from monas.commands.common import concurrency_option
from monas.config import Config, pass_config
from monas.project import PyPackage
from monas.utils import console, err_console, info, pip_install, run_command


def build_package(package: PyPackage, dist: Path, sdist: bool = False) -> str:
    # Install build tool
    venv_path = package.path / ".venv"
    pip_install(venv_path, ["build"])
    if os.name == "nt":
        python = venv_path / "Scripts" / "python.exe"
    else:
        python = venv_path / "bin" / "python"
    build_args = [str(python), "-m", "build", "--outdir", str(dist), "--wheel"]
    if sdist:
        build_args.append("--sdist")
    run_command(build_args, cwd=str(package.path), stdout=subprocess.DEVNULL)


@click.command()
@concurrency_option
@click.option(
    "--no-sdist", "sdist", flag_value=False, default=True, help="Do not build sdist"
)
@click.option("--username", "-u", help="PyPI username")
@click.option("--password", "-p", help="PyPI password or token")
@click.option("--repository", "-r", help="Repository name or URL")
@pass_config
@pass_context
def publish(
    ctx: click.Context,
    config: Config,
    *,
    concurrency: int,
    sdist: bool = True,
    username: str | None = None,
    password: str | None = None,
    repository: str | None = None,
):
    """Publish packages in this release to PyPI."""
    packages_to_publish = [
        pkg for pkg in config.iter_packages() if pkg.version == config.version
    ]
    if not packages_to_publish:
        info("No package to publish")
        return
    if repository is None:
        repo_args = []
        index = "[link]https://pypi.org/simple[/]"
    elif repository.startswith(("http://", "https://")):
        repo_args = ["--repository-url", repository]
        index = f"[link]{repository}[/]"
    else:
        repo_args = ["--repository", repository]
        index = f"[succ]{repository}[/]"
    info(f"The following packages are to be built and published to {index}:")
    for pkg in packages_to_publish:
        console.print(f"  [primary]{pkg.path.name}[/] [succ]{pkg.version}[/]")
    if not Confirm.ask("Continue?", console=console, default=True):
        ctx.abort()
    dist = config.path / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    dist.mkdir()
    with err_console.status(
        f"Building [primary]{len(packages_to_publish)}[/] package(s)", spinner="point"
    ):
        builder = functools.partial(build_package, dist=dist, sdist=sdist)
        with ThreadPoolExecutor(concurrency) as pool:
            pool.map(builder, packages_to_publish)
    twine_args = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--non-interactive",
        "dist/*",
    ]
    if username is not None:
        twine_args.extend(["--username", username])
    if password is not None:
        twine_args.extend(["--password", password])
    twine_args.extend(repo_args)
    with err_console.status(
        f"Publishing [primary]{len(packages_to_publish)}[/] package(s) to {index}",
        spinner="point",
    ):
        run_command(twine_args, cwd=str(config.path))
    info("[succ]Publish done[/]")
