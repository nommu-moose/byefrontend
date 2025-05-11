# ──── src/byefrontend/configs/secret.py ────
from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(slots=True, frozen=True)
class SecretToggleConfig(WidgetConfig):
    placeholder: str | None = None
    is_in_form: bool = False
