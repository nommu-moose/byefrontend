from dataclasses import dataclass
from .base import WidgetConfig


@dataclass(slots=True, frozen=True)
class TextInputConfig(WidgetConfig):
    """
    Configuration for widgets that ultimately render an <input> element
    (or a <textarea>) and do *not* add their own higher-level behaviour.

    All fields mirror vanilla HTML attributes so the widget can
    forward them verbatim into ``<input ...>`` without special-casing.
    """

    placeholder: str | None = None
    input_type: str = "text"           # e.g. "text", "password", "email"
    minlength: int | None = None
    maxlength: int | None = None
    pattern: str | None = None         # regexp pattern for front-end validation
    readonly: bool = False
    disabled: bool = False
    autocomplete: str | None = None    # e.g. "off" or "one-time-code"
    is_in_form: bool = False
