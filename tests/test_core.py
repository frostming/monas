import monas


def test_import_package():
    assert isinstance(monas.__all__, list)
