from nornir_rich import __version__


def test_version() -> None:
    assert __version__ == "0.2.0"  # From Makefile
