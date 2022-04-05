from typing import Any

import rich_click as click

from monas.commands.common import (
    filter_options,
    filter_packages,
    list_packages,
    output_options,
)
from monas.config import Config, pass_config
from monas.utils import info


@click.command("list")
@output_options
@filter_options
@pass_config
def list_command(config: Config, *, long: bool, json: bool, **kwargs: Any):
    """List packages managed by Monas. [yellow]alias: ls[/]"""
    packages = list(filter_packages(config, **kwargs))
    info(f"Found [primary]{len(packages)}[/] package(s)")
    list_packages(packages, long=long, json=json)
