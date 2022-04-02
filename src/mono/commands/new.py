from pathlib import Path

import rich_click as click
from rich.prompt import Confirm

from mono.config import Config, pass_config
from mono.project import InputMetadata, PyPackage
from mono.questions import ask_for, package_questions
from mono.utils import console, info


@click.command()
@click.argument("package", required=True)
@click.argument("location", required=False)
@pass_config
def new(config: Config, *, package: str, location: str | None = None):
    """Create a new <package> under <location>.

    The package name must be locally unique and available on PyPI.

    If location isn't given, it defaults to the first location of `packages` config.
    """
    if location is None:
        location = config.package_paths[0]
    if location not in config.package_paths:
        config.add_package_path(location)
    project_path = Path(location, package).absolute()
    repo = config.get_repo()

    default_values = {
        "name": package,
        "version": config.version,
        "author": repo.get_user_name(),
        "author_email": repo.get_user_email(),
        "homepage": f"{config.homepage}/packages/{package}"
        if config.homepage
        else None,
    }

    metadata = InputMetadata(
        remote_repo=repo.get_remote_url(),
        **ask_for(package_questions, **default_values),
    )
    pyproject = PyPackage(config, project_path)
    pyproject_doc = pyproject.build_toml(metadata)
    info(f"Writing pyproject.toml at [primary]{pyproject.toml_path}[/]:")
    console.print(pyproject_doc.as_string().replace("[", "\\["))
    if not Confirm.ask("Is this OK?", console=console, default=True):
        raise click.Abort()
    pyproject.write_toml(pyproject_doc)
    info("Creating project files")
    pyproject.create_project_files()
