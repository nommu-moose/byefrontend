from __future__ import annotations

from django import forms
from typing import Iterable

class TagListField(forms.Field):
    """Field that parses comma separated tags into a list of strings."""

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            return [t.strip() for t in value.split(',') if t.strip()]
        if isinstance(value, Iterable):
            tags: list[str] = []
            for val in value:
                if not val:
                    continue
                tags.extend(t.strip() for t in str(val).split(',') if t.strip())
            return tags
        return [str(value)]
