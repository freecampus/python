from __future__ import annotations

import fcpython


def test_package_exposes_version() -> None:
    assert isinstance(fcpython.__version__, str)
    assert fcpython.__version__
