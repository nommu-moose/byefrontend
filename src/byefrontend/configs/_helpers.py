"""
Internal helper utilities for the *configs* package.

The public symbols are **re-exported** from
`byefrontend.configs.__init__` so end-users never import from here
directly.
"""

from dataclasses import replace as _dc_replace
from typing import TypeVar

# generic parameter so mypy/pyright keep the type of the input
T = TypeVar("T")


def tweak(config_obj: T, /, **overrides) -> T:
    """
    Return a **new** frozen dataclass copied from *config_obj* with
    the supplied *overrides* applied.

    Example
    -------
    >>> from byefrontend.configs import SecretToggleConfig, tweak
    >>> secure_cfg = tweak(SecretToggleConfig(), label="API key", required=True)
    """
    return _dc_replace(config_obj, **overrides)
