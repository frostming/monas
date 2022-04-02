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


@click.group()
@click.version_option(__version__)
def main():
    """[cyan]Mono[/]: Python monorepo made easy"""


main.add_command(add)
main.add_command(init)
main.add_command(new)
main.add_command(install)
main.add_command(list_command)
main.add_command(list_command, "ls")
