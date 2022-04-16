from __future__ import annotations

from pathlib import Path

import rich_click as click
from click.decorators import pass_context
from rich.prompt import Confirm

from monas.config import Config, pass_config
from monas.project import InputMetadata, PyPackage, get_metadata_class_for_backend
from monas.questions import ask_for, package_questions
from monas.utils import console, info


@click.command()
@click.argument("package", required=True)
@click.argument("location", required=False)
@pass_config
@pass_context
def new(
    ctx: click.Context, config: Config, *, package: str, location: str | None = None
):
    """Create a new <package> under <location>.

    The package name must be locally unique and available on PyPI.

    If location isn't given, it defaults to the first location of `packages` config.
    """
    if location is None:
        location = config.package_paths[0]
    if any(package == pkg.path.name for pkg in config.iter_packages()):
        raise click.BadParameter(f"{package} already exists")
    package_path = Path(location, package).absolute()
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

    inputs = InputMetadata(
        remote_repo=repo.get_remote_url(),
        **ask_for(package_questions, **default_values),
    )
    metadata_cls = get_metadata_class_for_backend(inputs.build_backend)
    metadata_contents = metadata_cls.create(inputs)
    info(f"Writing pyproject.toml at [primary]{metadata_cls.filename}[/]:")
    console.print(metadata_contents.replace("[", "\\["))
    if not Confirm.ask("Is this OK?", console=console, default=True):
        ctx.abort()
    package_path.mkdir(parents=True)
    with package_path.joinpath(metadata_cls.filename).open("w", encoding="utf-8") as f:
        f.write(metadata_contents)
    info("Creating project files")
    PyPackage.create(config, package_path, inputs)
    if location not in config.package_paths:
        config.add_package_path(location)
