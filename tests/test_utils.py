import pytest

from monas.commands.bump import bump_version


@pytest.mark.parametrize(
    "original,part,tag,expected",
    [
        ("1.0.0", "major", None, "2.0.0"),
        ("1.0.0", "minor", None, "1.1.0"),
        ("1.0.0", "patch", None, "1.0.1"),
        ("1.0.0", None, "alpha", "1.0.0alpha0"),
        ("1.0.0", None, "dev", "1.0.0.dev0"),
        ("1.0.0", None, "post", "1.0.0.post0"),
        ("1.0.0", "major", "alpha", "2.0.0alpha0"),
        ("1.0.0alpha1", "major", None, "2.0.0"),
        ("1.0.0alpha1", "patch", None, "1.0.0"),
        ("1.0.0dev1", "patch", None, "1.0.0"),
        ("1.0.0a1", None, "a", "1.0.0a2"),
        ("1.0.0rc1", "patch", "rc", "1.0.1rc0"),
        ("1.0.0alpha1", None, "beta", "1.0.0beta0"),
        ("1.0.0alpha1", None, "dev", "1.0.0alpha1.dev0"),
    ],
)
def test_bump_version(original, part, tag, expected):
    assert bump_version(original, part, tag) == expected
