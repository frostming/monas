from unittest import mock

import pytest


@pytest.mark.parametrize("no_install", [True, False])
@mock.patch("monas.project.pip_install")
def test_add_dependency_to_all(pip_install, test_project, cli_run, no_install):
    cli_run(
        ["add", "click"] + (["--no-install"] if no_install else []), cwd=test_project
    )
    assert (
        "install_requires = \n\tclick"
        in (test_project / "packages/foo/setup.cfg").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )
    if no_install:
        pip_install.assert_not_called()
    else:
        pip_install.assert_has_calls(
            [
                mock.call(
                    test_project / "packages/foo/.venv",
                    ["-e {}".format((test_project / "packages/foo").as_posix())],
                ),
                mock.call(
                    test_project / "packages/bar/.venv",
                    ["-e {}".format((test_project / "packages/bar").as_posix())],
                ),
                mock.call(
                    test_project / "extras/foo-more/.venv",
                    ["-e {}".format((test_project / "extras/foo-more").as_posix())],
                ),
            ],
            any_order=True,
        )


@mock.patch("monas.project.pip_install")
def test_add_managed_package(pip_install, test_project, cli_run):
    cli_run(["add", "foo"], cwd=test_project)
    assert (
        'dependencies = [\n    "foo",\n]'
        in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        'dependencies = [\n    "foo",\n]'
        in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )
    pip_install.assert_has_calls(
        [
            mock.call(
                test_project / "packages/bar/.venv",
                [
                    "-e {}".format((test_project / "packages/foo").as_posix()),
                    "-e {}".format((test_project / "packages/bar").as_posix()),
                ],
            ),
            mock.call(
                test_project / "extras/foo-more/.venv",
                [
                    "-e {}".format((test_project / "packages/foo").as_posix()),
                    "-e {}".format((test_project / "extras/foo-more").as_posix()),
                ],
            ),
        ],
        any_order=True,
    )
    with pytest.raises(AssertionError):
        pip_install.assert_called_with(
            test_project / "packages/foo/.venv",
            ["-e {}".format((test_project / "packages/foo").as_posix())],
        )


@mock.patch("monas.project.pip_install")
def test_add_dependency_to_specific_packages(pip_install, test_project, cli_run):
    cli_run(["add", "click", "--include", "foo*"], cwd=test_project)
    assert (
        "install_requires = \n\tclick"
        in (test_project / "packages/foo/setup.cfg").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        not in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )
    pip_install.assert_has_calls(
        [
            mock.call(
                test_project / "packages/foo/.venv",
                ["-e {}".format((test_project / "packages/foo").as_posix())],
            ),
            mock.call(
                test_project / "extras/foo-more/.venv",
                ["-e {}".format((test_project / "extras/foo-more").as_posix())],
            ),
        ],
        any_order=True,
    )
    with pytest.raises(AssertionError):
        pip_install.assert_called_with(
            test_project / "packages/bar/.venv",
            ["-e {}".format((test_project / "packages/bar").as_posix())],
        )


@mock.patch("monas.project.pip_install")
def test_add_dependency_except_specific_packages(pip_install, test_project, cli_run):
    cli_run(["add", "click", "--exclude", "foo*"], cwd=test_project)
    assert (
        "install_requires = \n\tclick"
        not in (test_project / "packages/foo/setup.cfg").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        'dependencies = [\n    "click",\n]'
        not in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )
    pip_install.assert_called_once_with(
        test_project / "packages/bar/.venv",
        ["-e {}".format((test_project / "packages/bar").as_posix())],
    )
