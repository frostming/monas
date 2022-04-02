import mono


def test_import_package():
    assert isinstance(mono.__all__, list)
