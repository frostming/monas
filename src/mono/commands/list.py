from typing import Any

import rich_click as click
from rich.table import Table

from mono.commands.common import filter_options, filter_packages
from mono.config import Config, pass_config
from mono.utils import console


@click.command("list")
@click.option("--long", "-l", is_flag=True, default=False, help="Show the full path")
@filter_options
@pass_config
def list_command(config: Config, *, long: bool, **kwargs: Any):
    """List packages managed by Mono."""
    packages = filter_packages(config, **kwargs)
    table = Table.grid("Name", padding=(0, 1))
    if long:
        table.add_column("Version")
        table.add_column("Path")
    for pkg in packages:
        row = [f"[primary]{pkg.path.name}[/]"]
        if long:
            row.append(f"[succ]{pkg.version}[/]")
            row.append(f"[info]{pkg.path}[/]")
        table.add_row(*row)
    console.print(table)
