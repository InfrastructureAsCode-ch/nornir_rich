from nornir_rich import __version__


def test_version() -> None:
    assert __version__ == "0.1.5"  # From Makefile
