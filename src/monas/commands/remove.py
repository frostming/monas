from typing import Any, Collection

import rich_click as click
from click.decorators import pass_context
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name

from monas.commands.common import concurrency_option, filter_options, filter_packages
from monas.commands.install import install
from monas.config import Config, pass_config
from monas.utils import info


@click.command()
@click.option(
    "--no-install",
    "do_install",
    default=True,
    flag_value=False,
    help="Do not automatically chain [primary]monas install[/] after added",
)
@concurrency_option
@click.argument("dependency", required=True)
@filter_options
@pass_config
@pass_context
def remove(
    ctx: click.Context,
    config: Config,
    *,
    do_install: bool = True,
    concurrency: int,
    dependency: str,
    exclude: Collection[str],
    **kwargs: Any,
):
    """Remove a dependency from specified packages."""
    try:
        req = Requirement(dependency)
    except InvalidRequirement:
        raise click.BadParameter(f"Invalid dependency {dependency}")

    exclude = list(exclude) + [req.name]
    packages = list(filter_packages(config, exclude=exclude, **kwargs))
    if not packages:
        info("[notice]No package is found[/]")
        return

    info(
        f"Removing dependency [succ]{req.name}[/] from "
        f"[primary]{len(packages)}[/] package(s)"
    )
    for pkg in packages:
        pkg.remove_dependency(canonicalize_name(req.name))
    if do_install:
        ctx.invoke(
            install, concurrency=concurrency, root=False, exclude=exclude, **kwargs
        )
