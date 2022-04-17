from __future__ import annotations

import multiprocessing
from fnmatch import fnmatch
from typing import Collection, Iterable

import click
from rich.table import Table

from monas.config import Config
from monas.project import PyPackage
from monas.utils import console, is_relative_to


def filter_options(f):
    return click.option(
        "--include",
        help="[cyan](multiple)[/]Include packages matching the given glob",
        metavar="GLOB",
        multiple=True,
    )(
        click.option(
            "--exclude",
            help="[cyan](multiple)[/]Exclude packages matching the given glob",
            metavar="GLOB",
            multiple=True,
        )(f)
    )


def output_options(f):
    return click.option(
        "--long", "-l", is_flag=True, default=False, help="Show the full path"
    )(
        click.option(
            "--json", is_flag=True, default=False, help="Output in JSON format"
        )(f)
    )


concurrency_option = click.option(
    "--concurrency",
    "-c",
    default=multiprocessing.cpu_count(),
    type=int,
    help="The number of concurrent processes to use",
)


def filter_packages(
    config: Config, *, include: Collection[str], exclude: Collection[str]
) -> Iterable[PyPackage]:
    """Filter the packages with the include and exclude pattern."""
    for package in config.iter_packages():
        name = package.path.name
        if (include or any(fnmatch(name, pattern) for pattern in exclude)) and not any(
            fnmatch(name, pattern) for pattern in include
        ):
            continue
        yield package


def list_packages(
    packages: Iterable[PyPackage], *, long: bool = False, json: bool = False
) -> None:
    """List the packages."""
    if json:
        data = [
            {"name": pkg.path.name, "version": pkg.version, "path": pkg.path.as_posix()}
            for pkg in packages
        ]
        console.print_json(data=data)
        return
    table = Table.grid("Name", padding=(0, 1))
    if long:
        table.add_column("Version")
        table.add_column("Path", overflow="fold")
    for pkg in packages:
        row = [f"[primary]{pkg.path.name}[/]"]
        if long:
            row.append(f"[succ]{pkg.version}[/]")
            row.append(f"[info]{pkg.path.relative_to(pkg.config.path).as_posix()}[/]")
        table.add_row(*row)
    console.print(table)


def get_changed_packages(config: Config, describe_result: str) -> list[PyPackage]:
    """Get the changed packages."""
    repo = config.get_repo()
    if describe_result.tag and describe_result.distance == 0:
        return []
    packages = list(config.iter_packages())
    if describe_result.tag:
        diff_files = repo.diff(describe_result.tag)
        packages = [
            pkg
            for pkg in packages
            if any(is_relative_to(config.path / f, pkg.path) for f in diff_files)
        ]
    return packages
