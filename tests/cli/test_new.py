from unittest import mock

import pytest


@pytest.fixture()
def mock_input(backend):
    with mock.patch(
        "monas.commands.new.ask_for",
        return_value={
            "name": "foo",
            "version": "0.0.0",
            "author": "John",
            "author_email": "john@doe.me",
            "description": "Test Project",
            "license_expr": "MIT",
            "homepage": "https://example.org",
            "requires_python": ">=3.7",
            "build_backend": backend,
        },
    ):
        yield


pyproject_toml = """\
[project]
name = "foo"
version = "0.0.0"
description = "Test Project"
authors = [{name = "John", email = "john@doe.me"}]
requires-python = ">=3.7"
readme = "README.md"
dependencies = []
license = {text = "MIT"}

[project.urls]
Home = "https://example.org"
"""

setup_cfg = f"""\
[metadata]
name = foo
version = 0.0.0
description = Test Project
author = John
author_email = john@doe.me
license = MIT
long_description = file: README.md
long_description_content_type = text/markdown
project_urls ={' '}
\tHome = https://example.org

[options]
packages = find:
include_package_data = True
python_requires = >=3.7

"""

flit_backend = """
[build-system]
requires = ["flit_core>=3.2,<4"]
build-backend = "flit_core.buildapi"
"""

pdm_backend = """
[build-system]
requires = ["pdm-pep517"]
build-backend = "pdm.pep517.api"
"""

hatch_backend = """
[build-system]
requires = ["hatchling>=0.22.0"]
build-backend = "hatchling.build"
"""

setuptools_backend = """
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"
"""


@pytest.mark.parametrize(
    "backend,filename,content",
    [
        ("setuptools(setup.cfg)", "setup.cfg", setup_cfg),
        (
            "setuptools(pyproject.toml)",
            "pyproject.toml",
            pyproject_toml + setuptools_backend,
        ),
        ("pdm", "pyproject.toml", pyproject_toml + pdm_backend),
        ("flit", "pyproject.toml", pyproject_toml + flit_backend),
        ("hatch", "pyproject.toml", pyproject_toml + hatch_backend),
    ],
)
@pytest.mark.usefixtures("mock_input")
def test_new_package_with_backend(project, cli_run, filename, content):
    """
    Create a new project with a setuptools setup.cfg file.
    """
    cli_run(["new", "foo"], cwd=project, input="\n")
    package_path = project.joinpath("packages/foo")
    assert package_path.joinpath("foo").is_dir()
    assert package_path.joinpath("foo/__init__.py").is_file()
    assert package_path.joinpath(filename).read_text() == content, content
    assert (
        package_path.joinpath("README.md").read_text()
        == """\
# foo

Test Project

## Requirement

Python >=3.7

## Installation

```bash
pip install foo
```

## License

MIT
"""
    )


@pytest.mark.usefixtures("mock_input")
@pytest.mark.parametrize("backend", ["setuptools(setup.cfg)"])
def test_new_package_under_non_default_location(project, cli_run, python_version):
    """
    Create a new project in a non-default location.
    """
    cli_run(["new", "foo-bar", "others"], cwd=project, input="\n")
    package_path = project.joinpath("others/foo-bar")
    assert package_path.joinpath("foo_bar").is_dir()
    assert package_path.joinpath("foo_bar/__init__.py").is_file()
    assert (
        project.joinpath("pyproject.toml").read_text()
        == f"""\
[tool.monas]
packages = ["packages/", "others/"]
version = "0.0.0"
python-version = "{python_version}"
"""
    )
