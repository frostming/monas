from monas.utils import run_command


def test_bump_patch_version(test_project, cli_run):
    cli_run(["bump", "patch"], cwd=test_project, input="\n")
    result = cli_run(["list", "--long"], cwd=test_project)
    output_lines = sorted(line.strip().split() for line in result.output.splitlines())
    assert output_lines == [
        ["bar", "0.0.1", "packages/bar"],
        ["foo", "0.0.1", "packages/foo"],
        ["foo-more", "0.0.1", "extras/foo-more"],
    ]
    result = run_command(
        ["git", "describe"], cwd=str(test_project), capture_output=True
    )
    assert result.stdout.decode().strip() == "0.0.1"
