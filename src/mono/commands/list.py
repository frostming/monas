from typing import Any

import rich_click as click

from mono.commands.common import (
    filter_options,
    filter_packages,
    list_packages,
    output_options,
)
from mono.config import Config, pass_config
from mono.utils import info


@click.command("list")
@output_options
@filter_options
@pass_config
def list_command(config: Config, *, long: bool, json: bool, **kwargs: Any):
    """List packages managed by Mono. [yellow]alias: ls[/]"""
    packages = list(filter_packages(config, **kwargs))
    info(f"Found [primary]{len(packages)}[/] package(s)")
    list_packages(packages, long=long, json=json)
