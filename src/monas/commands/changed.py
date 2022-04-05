from __future__ import annotations

import rich_click as click

from monas.commands.common import get_changed_packages, list_packages, output_options
from monas.config import Config, pass_config
from monas.utils import info


@click.command()
@output_options
@pass_config
def changed(config: Config, *, long: bool, json: bool):
    """List packages changed since last tagged release."""
    describe_result = config.get_repo().describe_ref()
    packages = get_changed_packages(config, describe_result)
    if not packages:
        info(f"No change since last tag [succ]{describe_result.tag}[/]")
        return
    if not describe_result.tag:
        info("Assume all packages are changed since no release has been made")
    else:
        info(
            f"Found [primary]{len(packages)}[/] package(s) changed since "
            f"[succ]{describe_result.tag}[/]"
        )
    list_packages(packages, long=long, json=json)
