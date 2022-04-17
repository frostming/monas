import json

import pytest


@pytest.mark.parametrize("command", ["ls", "list"])
def test_list_packages(test_project, cli_run, command):
    result = cli_run([command], cwd=test_project)
    output_packages = [line.strip() for line in result.output.splitlines()]
    assert output_packages == ["foo", "bar", "foo-more"]


def test_list_packages_json_output(test_project, cli_run):
    result = cli_run(["list", "--json"], cwd=test_project)
    output_packages = json.loads(result.output)
    assert output_packages == [
        {
            "name": "foo",
            "version": "0.0.0",
            "path": (test_project / "packages/foo").as_posix(),
        },
        {
            "name": "bar",
            "version": "0.0.0",
            "path": (test_project / "packages/bar").as_posix(),
        },
        {
            "name": "foo-more",
            "version": "0.0.0",
            "path": (test_project / "extras/foo-more").as_posix(),
        },
    ]


def test_list_packages_long_output(test_project, cli_run):
    result = cli_run(["list", "--long"], cwd=test_project)
    output_lines = [line.strip().split() for line in result.output.splitlines()]
    assert output_lines == [
        ["foo", "0.0.0", "packages/foo"],
        ["bar", "0.0.0", "packages/bar"],
        ["foo-more", "0.0.0", "extras/foo-more"],
    ]
