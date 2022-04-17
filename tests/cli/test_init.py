def test_init_with_default_python_version(cli_run, tmp_path, python_version):
    cli_run(["init"], cwd=tmp_path)
    assert (
        tmp_path.joinpath("pyproject.toml").read_text()
        == f"""\
[tool.monas]
packages = ["packages/"]
version = "0.0.0"
python-version = "{python_version}"
"""
    )


def test_init_with_given_python_version(cli_run, tmp_path):
    cli_run(["init", "--python", "3.9"], cwd=tmp_path)
    assert (
        tmp_path.joinpath("pyproject.toml").read_text()
        == """\
[tool.monas]
packages = ["packages/"]
version = "0.0.0"
python-version = "3.9"
"""
    )
