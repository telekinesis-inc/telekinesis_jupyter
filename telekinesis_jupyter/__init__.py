
from pkg_resources import get_distribution
from line_magics import RemoteKernels

__version__ = get_distribution(__name__).version

__all__ = [
  "__version__",
  "RemoteKernels"
]