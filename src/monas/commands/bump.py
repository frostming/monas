from __future__ import annotations

import questionary
import rich_click as click
from click.decorators import pass_context
from parver import Version
from questionary.prompts.common import Choice
from rich.prompt import Confirm

from monas.commands.common import get_changed_packages
from monas.config import Config, pass_config
from monas.utils import console, info

# from parver import Version

PARTS = ["major", "minor", "patch"]
PRE_TAGS = ["alpha", "beta", "rc", "a", "b", "pre", "preview"]
POST_TAGS = ["post", "rev", "r"]
DEV_TAGS = ["dev"]


def bump_version(
    version_str: str, part: str | None = None, tag: str | None = None
) -> str:
    """Bump version based on the input part and tag"""
    version = Version.parse(version_str)
    if part is not None:
        if part == "patch" and tag is None and version.is_prerelease:
            version = version.replace(post=None, dev=None, pre=None)
        else:
            version = version.bump_release(index=PARTS.index(part)).replace(
                post=None, dev=None, pre=None
            )
    if tag is not None:
        if tag in PRE_TAGS:
            if tag != version.pre_tag and version.pre_tag is not None:
                version = version.replace(pre=None)
            version = version.bump_pre(tag)
        elif tag in POST_TAGS:
            if tag != version.post_tag and version.post_tag is not None:
                version = version.replace(post_tag=None)
            version = version.bump_post(tag)
        elif tag in DEV_TAGS:
            version = version.bump_dev()
        else:
            raise click.BadParameter(f"Unknown tag {tag}")
    return str(version)


@click.command()
@click.option("--skip-git", is_flag=True, help="Skip git operations")
@click.option("--message", "-m", help="Commit message")
@click.argument("part", required=False)
@click.argument("tag", required=False)
@pass_config
@pass_context
def bump(
    ctx: click.Context,
    config: Config,
    *,
    skip_git: bool,
    message: str | None,
    part: str | None,
    tag: str | None,
):
    """Bump version of all changed packages and release to git.

    [bold]Example[/]: [green]0.1.0[/]

    monas bump: [green]0.1.1[/]

    monas bump major: [green]1.0.0[/]

    monas bump minor: [green]0.2.0[/]

    monas bump patch: [green]0.1.1[/]

    monas bump alpha: [green]0.1.0alpha0[/]

    monas bump dev: [green]0.1.0dev0[/]

    monas bump post: [green]0.1.0post0[/]

    monas major alpha: [green]1.0.0alpha0[/]
    """
    repo = config.get_repo()
    describe_result = repo.describe_ref()
    packages = get_changed_packages(config, describe_result)

    if not packages:
        info("Current HEAD is already released, nothing to do")
        return

    version = config.version
    if part is None and tag is None:
        choices = {
            "patch": f'Patch ({bump_version(version, "patch")})',
            "minor": f'Minor ({bump_version(version, "minor")})',
            "major": f'Major ({bump_version(version, "major")})',
            "alpha": f'Alpha ({bump_version(version, None, "alpha")})',
            "minoralpha": f'MinorAlpha ({bump_version(version, "minor", "alpha")})',
            "majoralpha": f'MajorAlpha ({bump_version(version, "major", "alpha")})',
            "customprerelease": "Custom pre-release",
            "customversion": "Custom version",
        }
        prompt_choices = [Choice(value, key) for key, value in choices.items()]
        answer = questionary.select(
            "Select a version:",
            choices=prompt_choices,
            default=prompt_choices[0],
            pointer="▶",
        ).ask()
        if answer == "customprerelease":
            tag = questionary.select(
                "Select a prerelease tag:",
                choices=PRE_TAGS + POST_TAGS + DEV_TAGS,
                pointer="▶",
            ).ask()
            version = bump_version(version, part=None, tag=tag)
        elif answer == "customversion":
            version = questionary.text(
                "Enter a version:", instruction="(e.g. 1.2.3)"
            ).ask()
        else:
            version = choices[answer].split(" ", 1)[1][1:-1]

    else:
        if part and part not in PARTS:
            part, tag = None, part

        version = bump_version(version, part, tag)

    info(f"Will bump version for [primary]{len(packages)}[/] package(s)")
    for pkg in packages:
        console.print(
            f"  [primary]{pkg.path.name}[/] [succ]{pkg.version}[/] -> "
            f"[succ]{version}[/]"
        )
    if not Confirm.ask("Continue?", console=console, default=True):
        ctx.abort()
    for pkg in packages:
        pkg.set_version(version)
    config.set_version(version)
    info("[succ]Version updated[/]")
    if not skip_git:
        if not message:
            message = version
        repo.commit(message)
        repo.tag(version, version)
        if repo.get_remote_url() is not None:
            repo.push()
        info("[succ]Git repository updated[/]")
