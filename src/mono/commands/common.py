from __future__ import annotations
from fnmatch import fnmatch
import multiprocessing
from typing import Collection, Iterable
import click
from mono.project import PyPackage
from mono.config import Config


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
