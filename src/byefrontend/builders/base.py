"""
NOTE: forward references + TYPE_CHECKING let us keep full typing
    support while avoiding a runtime dependency on the widgets
    package.
"""
from __future__ import annotations

from types import MappingProxyType
from typing import Callable, Mapping, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from ..widgets.base import BFEBaseWidget
    from ..configs import WidgetConfig

T = TypeVar("T", bound="WidgetConfig")
BuilderFn = Callable[[T, "BFEBaseWidget | None"], "BFEBaseWidget"]


class ChildBuilderRegistry:
    """
    Global **registry** mapping *config* types → builder callables.
    Usage:

        @ChildBuilderRegistry.register(MyConfig)
        def _(cfg: MyConfig, parent):
            return MyWidget(config=cfg, parent=parent)
    """
    _registry: dict[type[WidgetConfig], BuilderFn] = {}

    @classmethod
    def register(cls, cfg_type: type[T]):
        def decorator(fn: BuilderFn) -> BuilderFn:
            cls._registry[cfg_type] = fn
            return fn
        return decorator

    @classmethod
    def build(
        cls,
        cfg: "WidgetConfig",
        parent: "BFEBaseWidget | None" = None,
    ) -> "BFEBaseWidget":
        try:
            builder = cls._registry[type(cfg)]
        except KeyError as exc:  # pragma: no cover
            raise ValueError(
                f"No builder registered for {type(cfg).__name__}"
            ) from exc
        return builder(cfg, parent)


def build_children(
    parent: "BFEBaseWidget",
    children_cfg: Mapping[str, "WidgetConfig"],
) -> Mapping[str, "BFEBaseWidget"]:
    """Return an *immutable* mapping: name → widget instance."""
    built = {
        name: ChildBuilderRegistry.build(cfg, parent)
        for name, cfg in children_cfg.items()
    }
    return MappingProxyType(built)
