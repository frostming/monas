from monas.utils import run_command


def test_show_changed_packages(test_project, cli_run):
    cli_run(["bump", "minor"], cwd=test_project, input="\n")
    result = cli_run(["changed"], cwd=test_project)
    assert result.stderr.strip() == "monas No change since last tag 0.1.0"
    # Do some changes
    test_project.joinpath("packages/foo/foo/utils.py").touch()
    run_command(["git", "add", "packages/foo/foo/utils.py"], cwd=str(test_project))
    run_command(["git", "commit", "-m", "Add utils.py"], cwd=str(test_project))
    # Show changed packages
    result = cli_run(["changed"], cwd=test_project)
    assert result.output.strip() == "foo"
