from __future__ import annotations

import rich_click as click
from rich import traceback

from mono.commands.add import add
from mono.commands.init import init
from mono.commands.install import install
from mono.commands.list import list_command
from mono.commands.new import new

__version__ = "0.1.0"

click.rich_click.USE_RICH_MARKUP = True
traceback.install()


class AliasGroup(click.RichGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aliases: dict[str, str] = {}

    def add_alias(self, alias: str, name: str) -> None:
        self.aliases[alias] = name

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        real_name = self.aliases.get(cmd_name, cmd_name)
        return super().get_command(ctx, real_name)


@click.group(cls=AliasGroup)
@click.version_option(__version__)
def main():
    """[cyan]Mono[/]: Python monorepo made easy"""


main.add_command(add)
main.add_command(init)
main.add_command(new)
main.add_command(install)
main.add_command(list_command)
main.add_alias("ls", "list")
