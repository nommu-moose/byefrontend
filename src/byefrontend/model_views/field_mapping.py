"""
Automatic mapping from Django model fields to BFE WidgetConfigs.

This module introspects Django model fields and generates appropriate
widget configurations for rendering forms, detail views, and list views.
"""
from __future__ import annotations

from typing import Any, Callable, Type, TYPE_CHECKING

from django.db import models

from ..configs import (
    WidgetConfig,
    TextInputConfig,
    TextEditorConfig,
    CheckBoxConfig,
    DatePickerConfig,
    DropdownConfig,
    FileUploadConfig,
    LabelConfig,
)

if TYPE_CHECKING:
    pass


# Type alias for config factories
ConfigFactory = Callable[[models.Field], WidgetConfig] | Type[WidgetConfig]


def _text_input_factory(field: models.Field) -> TextInputConfig:
    """Generate TextInputConfig with appropriate constraints from CharField."""
    return TextInputConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        maxlength=getattr(field, 'max_length', None),
        placeholder=f"Enter {field.verbose_name}" if field.verbose_name else None,
    )


def _email_input_factory(field: models.Field) -> TextInputConfig:
    """Generate TextInputConfig for email fields."""
    return TextInputConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        input_type="email",
        placeholder=f"Enter {field.verbose_name}" if field.verbose_name else None,
    )


def _url_input_factory(field: models.Field) -> TextInputConfig:
    """Generate TextInputConfig for URL fields."""
    return TextInputConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        input_type="url",
        placeholder=f"Enter {field.verbose_name}" if field.verbose_name else None,
    )


def _number_input_factory(field: models.Field) -> TextInputConfig:
    """Generate TextInputConfig for numeric fields."""
    return TextInputConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        input_type="number",
        placeholder=f"Enter {field.verbose_name}" if field.verbose_name else None,
    )


def _textarea_factory(field: models.Field) -> TextEditorConfig:
    """Generate TextEditorConfig for TextField."""
    return TextEditorConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        placeholder=f"Enter {field.verbose_name}" if field.verbose_name else None,
    )


def _checkbox_factory(field: models.Field) -> CheckBoxConfig:
    """Generate CheckBoxConfig for BooleanField."""
    return CheckBoxConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        checked=field.default if field.default is not models.NOT_PROVIDED else False,
    )


def _date_factory(field: models.Field) -> DatePickerConfig:
    """Generate DatePickerConfig for DateField/DateTimeField."""
    return DatePickerConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
    )


def _foreign_key_factory(field: models.ForeignKey) -> DropdownConfig:
    """
    Generate DropdownConfig for ForeignKey fields.
    
    Note: Choices are populated lazily at render time to avoid
    database queries during import.
    """
    return DropdownConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        placeholder=f"Select {field.verbose_name}" if field.verbose_name else "Select...",
        choices=(),  # Populated at render time
    )


def _choice_field_factory(field: models.Field) -> DropdownConfig:
    """Generate DropdownConfig for fields with choices."""
    choices = tuple(field.choices) if field.choices else ()
    return DropdownConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
        choices=choices,
        placeholder=f"Select {field.verbose_name}" if field.verbose_name else "Select...",
    )


def _file_field_factory(field: models.Field) -> FileUploadConfig:
    """Generate FileUploadConfig for FileField/ImageField."""
    return FileUploadConfig(
        name=field.name,
        label=field.verbose_name.title() if field.verbose_name else field.name,
        required=not field.blank,
        help_text=field.help_text or None,
    )


def _readonly_factory(field: models.Field) -> LabelConfig:
    """Generate LabelConfig for readonly/auto fields."""
    return LabelConfig(
        name=field.name,
        text=field.verbose_name.title() if field.verbose_name else field.name,
    )


# Main mapping from Django field types to config factories
FIELD_TO_CONFIG: dict[Type[models.Field], ConfigFactory] = {
    # Text fields
    models.CharField: _text_input_factory,
    models.TextField: _textarea_factory,
    models.EmailField: _email_input_factory,
    models.URLField: _url_input_factory,
    models.SlugField: _text_input_factory,
    
    # Numeric fields
    models.IntegerField: _number_input_factory,
    models.SmallIntegerField: _number_input_factory,
    models.BigIntegerField: _number_input_factory,
    models.PositiveIntegerField: _number_input_factory,
    models.PositiveSmallIntegerField: _number_input_factory,
    models.PositiveBigIntegerField: _number_input_factory,
    models.FloatField: _number_input_factory,
    models.DecimalField: _number_input_factory,
    
    # Boolean
    models.BooleanField: _checkbox_factory,
    models.NullBooleanField: _checkbox_factory,
    
    # Date/Time
    models.DateField: _date_factory,
    models.DateTimeField: _date_factory,
    models.TimeField: _text_input_factory,  # Could be a TimePicker widget later
    
    # Relations
    models.ForeignKey: _foreign_key_factory,
    
    # Files
    models.FileField: _file_field_factory,
    models.ImageField: _file_field_factory,
    
    # Auto fields (readonly)
    models.AutoField: _readonly_factory,
    models.BigAutoField: _readonly_factory,
    models.SmallAutoField: _readonly_factory,
}


def config_for_field(
    field: models.Field,
    *,
    readonly: bool = False,
    widget_override: WidgetConfig | None = None,
) -> WidgetConfig:
    """
    Generate a WidgetConfig from a Django model field.
    
    Args:
        field: The Django model field to generate config for.
        readonly: If True, generates a LabelConfig for display only.
        widget_override: If provided, returns this config instead
                        (with name/label populated from field if not set).
    
    Returns:
        A WidgetConfig appropriate for the field type.
    """
    # If override provided, use it (but fill in name if missing)
    if widget_override is not None:
        return widget_override
    
    # Readonly fields get label display
    if readonly:
        return _readonly_factory(field)
    
    # Fields with explicit choices get dropdown
    if field.choices:
        return _choice_field_factory(field)
    
    # Look up by field type
    field_type = type(field)
    
    # Try exact match first
    if field_type in FIELD_TO_CONFIG:
        factory = FIELD_TO_CONFIG[field_type]
        if callable(factory) and not isinstance(factory, type):
            return factory(field)
        return factory(
            name=field.name,
            label=field.verbose_name.title() if field.verbose_name else field.name,
            required=not field.blank,
            help_text=field.help_text or None,
        )
    
    # Try MRO for inherited field types
    for base_type in field_type.__mro__:
        if base_type in FIELD_TO_CONFIG:
            factory = FIELD_TO_CONFIG[base_type]
            if callable(factory) and not isinstance(factory, type):
                return factory(field)
            return factory(
                name=field.name,
                label=field.verbose_name.title() if field.verbose_name else field.name,
                required=not field.blank,
                help_text=field.help_text or None,
            )
    
    # Fallback to text input
    return _text_input_factory(field)


def configs_for_model(
    model: Type[models.Model],
    *,
    fields: tuple[str, ...] | list[str] | None = None,
    exclude: tuple[str, ...] | list[str] = (),
    readonly_fields: tuple[str, ...] | list[str] = (),
    widget_overrides: dict[str, WidgetConfig] | None = None,
    include_pk: bool = False,
) -> dict[str, WidgetConfig]:
    """
    Generate a mapping of field names to WidgetConfigs for a Django model.
    
    Args:
        model: The Django model class.
        fields: Specific fields to include (None = all editable fields).
        exclude: Field names to exclude.
        readonly_fields: Fields to render as readonly (LabelConfig).
        widget_overrides: Dict of field_name -> WidgetConfig overrides.
        include_pk: Whether to include primary key field.
    
    Returns:
        Dict mapping field names to their generated WidgetConfigs.
    """
    widget_overrides = widget_overrides or {}
    exclude_set = set(exclude)
    readonly_set = set(readonly_fields)
    
    # Get all concrete fields from the model
    model_fields = {f.name: f for f in model._meta.get_fields() if hasattr(f, 'name')}
    
    # Determine which fields to include
    if fields is not None:
        field_names = list(fields)
    else:
        # Default: all concrete, editable fields
        field_names = [
            f.name for f in model._meta.get_fields()
            if (
                hasattr(f, 'name') and
                hasattr(f, 'editable') and
                f.editable and
                not f.primary_key
            )
        ]
    
    # Include pk if requested
    if include_pk:
        pk_name = model._meta.pk.name if model._meta.pk else 'pk'
        if pk_name not in field_names:
            field_names.insert(0, pk_name)
    
    # Build configs
    configs: dict[str, WidgetConfig] = {}
    
    for name in field_names:
        if name in exclude_set:
            continue
            
        field = model_fields.get(name)
        if field is None:
            continue
            
        # Skip reverse relations and many-to-many for now
        if isinstance(field, (models.ManyToOneRel, models.ManyToManyRel, models.ManyToManyField)):
            continue
        
        configs[name] = config_for_field(
            field,
            readonly=name in readonly_set,
            widget_override=widget_overrides.get(name),
        )
    
    return configs


def get_foreign_key_choices(field: models.ForeignKey, queryset=None) -> tuple[tuple[str, str], ...]:
    """
    Get choices for a ForeignKey field.
    
    Args:
        field: The ForeignKey field.
        queryset: Optional queryset to use instead of all objects.
    
    Returns:
        Tuple of (pk, str_representation) pairs.
    """
    related_model = field.related_model
    qs = queryset if queryset is not None else related_model.objects.all()
    
    return tuple(
        (str(obj.pk), str(obj))
        for obj in qs
    )

