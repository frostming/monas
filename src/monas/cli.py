from __future__ import annotations

import rich_click as click
from rich import traceback

from monas.commands.add import add
from monas.commands.bump import bump
from monas.commands.changed import changed
from monas.commands.init import init
from monas.commands.install import install
from monas.commands.list import list_command
from monas.commands.new import new
from monas.commands.publish import publish
from monas.commands.remove import remove
from monas.utils import err_console

__version__ = "0.0.3"

click.rich_click.USE_RICH_MARKUP = True
traceback.install(console=err_console)


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
    """[cyan]Monas[/]: Python monorepo made easy"""


main.add_command(add)
main.add_command(bump)
main.add_command(changed)
main.add_command(init)
main.add_command(install)
main.add_command(list_command)
main.add_alias("ls", "list")
main.add_command(new)
main.add_command(publish)
main.add_command(remove)
