from __future__ import annotations

import textwrap
from pathlib import Path

import rich_click as click
import tomlkit
from tomlkit.toml_file import TOMLFile

from monas.utils import get_preferred_python_version, info


@click.command()
@click.option(
    "-p",
    "--python",
    "python_version",
    metavar="PYTHON_VERSION",
    default=get_preferred_python_version(),
    help="The Python version to use",
)
@click.option("-v", "--version", default="0.0.0", help="The version of the monorepo")
@click.option(
    "-d",
    "--default-package-dir",
    multiple=True,
    default=["packages"],
    help="Default Package Directories to be created",
)
@click.option(
    "-n",
    "--no-package-dir",
    is_flag=True,
    default=False,
    help="If specified, no package directories will be created",
)
def init(
    *,
    version: str,
    python_version: str,
    default_package_dir: list[str],
    no_package_dir: bool,
) -> None:
    """Initialize the monas tool.

    Args:
        path: The path to the `pyproject.toml` file.
    """
    default_package_dirs = list(default_package_dir)
    if no_package_dir:
        default_package_dirs.clear()
    mono_settings = {
        "packages": [f"{pb}/*" for pb in default_package_dirs],
        "version": version,
        "python-version": python_version,
    }
    pyproject_toml = Path("pyproject.toml")
    if pyproject_toml.exists():
        verb = "Updating"
        doc = TOMLFile(pyproject_toml).read()
    else:
        verb = "Creating"
        doc = {}
    info(f"{verb} {pyproject_toml.name}")
    doc.setdefault("tool", {}).setdefault("monas", {}).update(mono_settings)
    pyproject_toml.write_text(tomlkit.dumps(doc))
    for p in default_package_dirs:
        p = Path(p)
        if not p.exists():
            info(f"Creating {p.name}")
            p.mkdir(parents=True)
    info("Creating project files")
    protect_setup_py = Path("setup.py")
    protect_setup_py.write_text(
        textwrap.dedent(
            '''\
        """
        This is a protect setup.py file to prevent the parent project
        from being built or uploaded.
        """
        raise RuntimeError("The parent project should never be built nor uploaded.")
        '''
        )
    )
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        gitignore.write_text(
            textwrap.dedent(
                """\
            __pycache__/
            *.py[cod]
            .pytest_cache/
            .pdm.toml
            build/
            /dist/
            *.egg-info/
            .envrc
            .direnv/
            """
            )
        )
