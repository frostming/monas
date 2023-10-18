def test_init_with_default_python_version(cli_run, tmp_path, python_version):
    cli_run(["init"], cwd=tmp_path)
    assert (
        tmp_path.joinpath("pyproject.toml").read_text()
        == f"""\
[tool.monas]
packages = ["packages/*"]
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
packages = ["packages/*"]
version = "0.0.0"
python-version = "3.9"
"""
    )


def test_init_with_no_package_directories(cli_run, tmp_path):
    cli_run(["init", "-n", "-p", "3.9"], cwd=tmp_path)
    assert (
        tmp_path.joinpath("pyproject.toml").read_text()
        == """\
[tool.monas]
packages = []
version = "0.0.0"
python-version = "3.9"
"""
    )


def test_init_with_selected_package_directories(cli_run, tmp_path):
    cli_run(["init", "-p", "3.9", "-d", "packages1", "-d", "packages2"], cwd=tmp_path)
    print("CLI TEST_RAN")
    assert (
        tmp_path.joinpath("pyproject.toml").read_text()
        == """\
[tool.monas]
packages = ["packages1/*", "packages2/*"]
version = "0.0.0"
python-version = "3.9"
"""
    )
    import os

    assert os.path.exists(os.path.join(tmp_path, "packages1"))
    assert os.path.exists(os.path.join(tmp_path, "packages2"))
