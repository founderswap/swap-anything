from packaging.version import Version
from pydantic import __version__

from ._base import BackendType

if Version(__version__) < Version("2.0"):  # pragma: no cover
    raise Exception("Swapanything Backend requires pydantic>=2.0")
