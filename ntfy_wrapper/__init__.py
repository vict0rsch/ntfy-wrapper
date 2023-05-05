from .notifier import Notifier  # noqa: F401

import importlib.metadata as met


__version__ = met.version("ntfy_wrapper")

del met
