"""Configuration for the pytest test suite."""
import os
from unittest import mock

import pytest
from click.testing import CliRunner

from monas.cli import main
from monas.utils import get_preferred_python_version, run_command


@pytest.fixture()
def cli_run():
    """Run the CLI."""
    runner = CliRunner(mix_stderr=False)

    def invoke(args, catch_exceptions=False, cwd=None, **kwargs):
        """Run the CLI."""
        curdir = os.getcwd()
        if cwd is not None:
            os.chdir(cwd)
        try:
            return runner.invoke(
                main, args, catch_exceptions=catch_exceptions, **kwargs
            )
        finally:
            os.chdir(curdir)

    return invoke


@pytest.fixture()
def project(tmp_path, cli_run):
    """
    Create a new project in the given path.
    """
    cli_run(["init"], cwd=tmp_path)
    return tmp_path


@pytest.fixture()
def python_version():
    return get_preferred_python_version()


@pytest.fixture()
def test_project(cli_run, project):
    run_command(["git", "init"], cwd=str(project))
    with mock.patch(
        "monas.commands.new.ask_for",
        side_effect=[
            {
                "name": "foo",
                "version": "0.0.0",
                "author": "John",
                "author_email": "john@doe.me",
                "description": "Test Project",
                "license_expr": "MIT",
                "homepage": "https://example.org",
                "requires_python": ">=3.7",
                "build_backend": backend,
            }
            for backend in ["setuptools(setup.cfg)", "pdm", "flit"]
        ],
    ):
        cli_run(["new", "foo"], cwd=project, input="\n")
        cli_run(["new", "bar"], cwd=project, input="\n")
        cli_run(["new", "foo-more", "extras"], cwd=project, input="\n")
    run_command(["git", "add", "."], cwd=str(project))
    run_command(["git", "commit", "-m", "Initial commit"], cwd=str(project))
    return project
