"""
Generic helpers for *derived* (read-only) state that should be
constructed once during __init__ and then left untouched.

Usage pattern
-------------
from byefrontend.builders import build_children, ChildBuilderRegistry

class MyWidget(BFEBaseWidget):
    def __init__(...):
        super().__init__(...)
        # 🔑  Derived, immutable mapping
        self._children = build_children(self, self.cfg.children)
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Callable, Dict, Mapping, TypeVar

from ..configs.base import WidgetConfig
from ..widgets.base import BFEBaseWidget

T = TypeVar("T", bound=WidgetConfig)
BuilderFn = Callable[[T, BFEBaseWidget | None], BFEBaseWidget]


class ChildBuilderRegistry:
    """
    Global **registry** mapping *config* types → *builder* callables.

    Register new widget families with the provided decorator:

    ```python
    @ChildBuilderRegistry.register(MyConfig)
    def _(cfg: MyConfig, parent):
        return MyWidget(config=cfg, parent=parent)
    ```
    """
    _builders: Dict[type, BuilderFn] = {}

    @classmethod
    def register(cls, cfg_type: type[T]):
        def decorator(fn: BuilderFn) -> BuilderFn:
            cls._builders[cfg_type] = fn
            return fn
        return decorator

    @classmethod
    def build(cls, cfg: WidgetConfig, parent: BFEBaseWidget) -> BFEBaseWidget:
        for cfg_type, builder in cls._builders.items():
            if isinstance(cfg, cfg_type):
                return builder(cfg, parent)
        raise TypeError(f"No builder registered for config type {type(cfg)}")


def build_children(
    parent: BFEBaseWidget,
    children_cfg: Mapping[str, WidgetConfig],
) -> Mapping[str, BFEBaseWidget]:
    """Return an **immutable** mapping `name → widget instance`."""
    realised = {
        name: ChildBuilderRegistry.build(cfg, parent)
        for name, cfg in children_cfg.items()
    }
    return MappingProxyType(realised)
