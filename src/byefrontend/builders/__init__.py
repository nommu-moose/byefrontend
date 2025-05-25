"""
Generic helpers for *derived* (read-only) state that should be
constructed once during __init__ and then left untouched.

Usage pattern

from byefrontend.builders import build_children, ChildBuilderRegistry

class MyWidget(BFEBaseWidget):
    def __init__(...):
        super().__init__(...)
        # 🔑  Derived, immutable mapping
        self._children = build_children(self, self.cfg.children)
"""

from .base import ChildBuilderRegistry, build_children


__all__: tuple[str, ...] = [
    "ChildBuilderRegistry",
    "build_children"
]
