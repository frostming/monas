def test_remove_dependency(test_project, cli_run):
    cli_run(["add", "click", "--no-install"], cwd=test_project)
    cli_run(["remove", "click", "--no-install"], cwd=test_project)
    assert (
        "install_requires = \n\tclick"
        not in (test_project / "packages/foo/setup.cfg").read_text()
    )
    assert (
        "dependencies = []"
        in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        "dependencies = []"
        in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )


def test_remove_managed_package(test_project, cli_run):
    cli_run(["add", "foo", "--no-install"], cwd=test_project)
    cli_run(["remove", "foo", "--no-install"], cwd=test_project)
    assert (
        "dependencies = []"
        in (test_project / "packages/bar/pyproject.toml").read_text()
    )
    assert (
        "dependencies = []"
        in (test_project / "extras/foo-more/pyproject.toml").read_text()
    )
