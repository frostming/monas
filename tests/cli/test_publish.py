import sys
from unittest import mock


@mock.patch("monas.commands.publish.build_package")
@mock.patch("monas.commands.publish.run_command")
def test_publish(run_command, build_package, test_project, cli_run):
    cli_run(["publish"], cwd=test_project, input="\n")
    assert build_package.call_count == 3
    twine_args = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--non-interactive",
        "dist/*",
    ]
    run_command.assert_called_once_with(twine_args, cwd=str(test_project))
