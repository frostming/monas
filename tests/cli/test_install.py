from unittest import mock


@mock.patch("monas.project.pip_install")
def test_install_all_packages(pip_install, test_project, cli_run):
    cli_run(["add", "click", "--no-install"], cwd=test_project)
    cli_run(["install"], cwd=test_project)
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
@mock.patch("monas.commands.install.pip_install")
def test_install_packages_to_root(root_install, package_install, test_project, cli_run):
    cli_run(["add", "click", "--no-install"], cwd=test_project)
    cli_run(["install", "--root"], cwd=test_project)
    package_install.assert_not_called()
    root_install.assert_called_once_with(test_project / ".venv", mock.ANY)
