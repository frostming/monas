from __future__ import annotations

from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor as Pool
from typing import Any

import rich_click as click

from monas.commands.common import concurrency_option, filter_options, filter_packages
from monas.config import Config, pass_config
from monas.project import PyPackage
from monas.utils import err_console as console
from monas.utils import info, pip_install, sh_join


@click.command()
@concurrency_option
@click.option(
    "--root",
    is_flag=True,
    default=False,
    help="Install all packages into the root project",
)
@filter_options
@pass_config
def install(config: Config, *, concurrency: int, root: bool, **kwargs: Any) -> None:
    """Link the packages and install the remaining dependencies."""
    packages = list(filter_packages(config, **kwargs))
    package_count = len(packages)

    if not packages:
        info("[notice]No package is found[/]")
        return

    if root:
        with console.status(
            f"Installing [primary]{package_count}[/] package(s) to the root project",
            spinner="point",
        ):
            requirements = (sh_join(["-e", pkg.path.as_posix()]) for pkg in packages)
            pip_install(config.root_venv, requirements)
        info("[succ]Installation done[/]")
        return
    errors: list[BaseException] = []

    def _on_complete(project: PyPackage, future: Future) -> None:
        if future.exception():
            console.print(
                f" [red bold]FAIL[/] {project.path.name} {future.exception()}"
            )
            errors.append(future.exception())
        else:
            console.print(f" [succ]SUCC[/] {project.path.name}")

    with console.status(
        f"Installing [primary]{package_count}[/] package(s)", spinner="point"
    ):
        with Pool(concurrency) as executor:
            for pkg in packages:
                future = executor.submit(pkg.install)
                future.add_done_callback(lambda f, pkg=pkg: _on_complete(pkg, f))
    info("[danger]Some packages failed[/]" if errors else "[succ]All succeeded[/]")
