"""
BFEModelView - Base class for declarative model view configuration.

Similar to Django's ModelAdmin, but generates BFE widgets for rendering.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Sequence, Type

from django.db import models
from django.db.models import QuerySet

from .field_mapping import configs_for_model, get_foreign_key_choices

if TYPE_CHECKING:
    from ..widgets.base import BFEBaseWidget
    from ..widgets.form import BFEFormWidget
    from ..configs.base import WidgetConfig


class BFEModelView:
    """
    Declarative configuration for rendering a Django model with BFE widgets.
    
    Similar to ModelAdmin, define class attributes to customize how
    the model is displayed in list, detail, and form views.
    
    Example:
        @bfe.register(Article)
        class ArticleView(BFEModelView):
            list_fields = ('title', 'author', 'published_date')
            list_filters = ('author', 'published_date')
            
            detail_layout = SectionConfig(
                title="Article Details",
                fields=('title', 'author', 'content', 'published_date'),
            )
    """
    
    # The Django model class - set by registry or subclass
    model: Type[models.Model] | None = None
    
    # ===== List View Configuration =====
    list_fields: tuple[str, ...] | list[str] | None = None  # None = all fields
    list_layout: str | WidgetConfig = "table"  # "table" | "cards" | LayoutConfig
    list_widgets: dict[str, WidgetConfig] = {}  # Field-specific widget overrides
    list_per_page: int = 25
    list_filters: tuple[str, ...] | list[str] = ()  # Fields to add as filters
    list_search_fields: tuple[str, ...] | list[str] = ()  # Fields to search
    list_ordering: tuple[str, ...] | list[str] | None = None  # Default ordering
    
    # ===== Detail View Configuration =====
    detail_fields: tuple[str, ...] | list[str] | None = None
    detail_layout: WidgetConfig | None = None  # None = auto-generate
    detail_widgets: dict[str, WidgetConfig] = {}
    
    # ===== Form View Configuration (create/update) =====
    form_fields: tuple[str, ...] | list[str] | None = None
    form_layout: WidgetConfig | None = None
    form_widgets: dict[str, WidgetConfig] = {}
    
    # ===== Shared Configuration =====
    readonly_fields: tuple[str, ...] | list[str] = ()
    exclude: tuple[str, ...] | list[str] = ()
    
    # ===== Hooks =====
    
    def get_queryset(self, request) -> QuerySet:
        """
        Return the queryset for list views.
        Override to add custom filtering/ordering.
        """
        qs = self.model.objects.all()
        if self.list_ordering:
            qs = qs.order_by(*self.list_ordering)
        return qs
    
    def get_object(self, request, pk) -> models.Model:
        """
        Return a single model instance.
        Override for custom object retrieval logic.
        """
        return self.model.objects.get(pk=pk)
    
    # ===== Widget Generation =====
    
    def get_list_fields(self) -> tuple[str, ...]:
        """Get the fields to display in list view."""
        if self.list_fields is not None:
            return tuple(self.list_fields)
        
        # Default: all concrete fields except large text fields
        return tuple(
            f.name for f in self.model._meta.get_fields()
            if (
                hasattr(f, 'name') and
                hasattr(f, 'concrete') and
                f.concrete and
                not isinstance(f, models.TextField)
            )
        )[:8]  # Limit to first 8 fields for readability
    
    def get_detail_fields(self) -> tuple[str, ...]:
        """Get the fields to display in detail view."""
        if self.detail_fields is not None:
            return tuple(self.detail_fields)
        
        # Default: all concrete fields
        return tuple(
            f.name for f in self.model._meta.get_fields()
            if hasattr(f, 'name') and hasattr(f, 'concrete') and f.concrete
        )
    
    def get_form_fields(self) -> tuple[str, ...]:
        """Get the fields to display in form view."""
        if self.form_fields is not None:
            return tuple(self.form_fields)
        
        # Default: all editable fields
        return tuple(
            f.name for f in self.model._meta.get_fields()
            if (
                hasattr(f, 'name') and
                hasattr(f, 'editable') and
                f.editable and
                not f.primary_key
            )
        )
    
    def get_list_widget(self, queryset: QuerySet, request) -> BFEBaseWidget:
        """
        Generate the widget for list view.
        
        Returns a DataFilterWidget or TableWidget based on configuration.
        """
        from ..configs import TableConfig, DataFilterConfig, TextInputConfig, CheckBoxConfig, DropdownConfig
        from ..widgets import TableWidget, DataFilterWidget
        
        fields = self.get_list_fields()
        
        # Build table field definitions
        table_fields = []
        for field_name in fields:
            model_field = self.model._meta.get_field(field_name)
            table_fields.append({
                "field_name": field_name,
                "field_text": model_field.verbose_name.title() if hasattr(model_field, 'verbose_name') else field_name,
                "field_type": "text",
            })
        
        # Build data from queryset
        data = list(queryset.values(*fields))
        
        # Build filters if specified
        if self.list_filters or self.list_search_fields:
            filter_configs = {}
            
            # Add search field
            if self.list_search_fields:
                filter_configs['search'] = TextInputConfig(
                    label="Search",
                    placeholder="Search...",
                )
            
            # Add filters for specified fields
            for filter_field in self.list_filters:
                model_field = self.model._meta.get_field(filter_field)
                
                if isinstance(model_field, models.BooleanField):
                    filter_configs[filter_field] = CheckBoxConfig(
                        label=model_field.verbose_name.title(),
                    )
                elif isinstance(model_field, models.ForeignKey) or model_field.choices:
                    choices = model_field.choices if model_field.choices else get_foreign_key_choices(model_field)
                    filter_configs[filter_field] = DropdownConfig(
                        label=model_field.verbose_name.title(),
                        choices=choices,
                        placeholder=f"Filter by {model_field.verbose_name}",
                    )
                else:
                    filter_configs[filter_field] = TextInputConfig(
                        label=model_field.verbose_name.title(),
                        placeholder=f"Filter by {model_field.verbose_name}",
                    )
            
            config = DataFilterConfig(
                filters=filter_configs,
                data=data,
                table_fields=table_fields,
                page_size=self.list_per_page,
            )
            return DataFilterWidget(config=config, request=request)
        
        # Simple table without filters
        config = TableConfig(
            fields=table_fields,
            data=data,
        )
        return TableWidget(config=config)
    
    def get_detail_widget(self, instance: models.Model, request) -> BFEBaseWidget:
        """
        Generate the widget for detail view.
        
        Uses detail_layout if specified, otherwise auto-generates
        a CardWidget with all fields.
        """
        from ..configs import CardConfig, LabelConfig
        from ..widgets import CardWidget
        from ..builders import build_children
        
        # If custom layout specified, use it (with field resolution)
        if self.detail_layout is not None:
            return self._resolve_layout(self.detail_layout, instance, readonly=True)
        
        # Auto-generate: Card with labels for each field
        fields = self.get_detail_fields()
        children_cfg = {}
        
        for field_name in fields:
            if field_name in self.exclude:
                continue
                
            value = getattr(instance, field_name, None)
            
            # Handle related fields
            if hasattr(value, '__str__'):
                display_value = str(value) if value is not None else "—"
            else:
                display_value = str(value) if value is not None else "—"
            
            model_field = self.model._meta.get_field(field_name)
            label = model_field.verbose_name.title() if hasattr(model_field, 'verbose_name') else field_name
            
            # Use override if provided
            if field_name in self.detail_widgets:
                children_cfg[field_name] = self.detail_widgets[field_name]
            else:
                children_cfg[field_name] = LabelConfig(
                    name=field_name,
                    text=f"{label}: {display_value}",
                )
        
        config = CardConfig(
            title=str(instance),
            children=children_cfg,
        )
        return CardWidget(config=config)
    
    def get_form_widget(self, request, instance: models.Model | None = None) -> BFEFormWidget:
        """
        Generate the widget for create/update forms.
        
        Uses form_layout if specified, otherwise auto-generates
        a form with appropriate widgets for each field.
        """
        from ..configs import FormConfig
        from ..widgets import BFEFormWidget
        from django.urls import reverse
        
        fields = self.get_form_fields()
        
        # Generate configs for form fields
        children_cfg = configs_for_model(
            self.model,
            fields=fields,
            exclude=self.exclude,
            readonly_fields=self.readonly_fields,
            widget_overrides=self.form_widgets,
        )
        
        # Populate ForeignKey choices
        for field_name, cfg in children_cfg.items():
            model_field = self.model._meta.get_field(field_name)
            if isinstance(model_field, models.ForeignKey):
                from dataclasses import replace
                from ..configs import DropdownConfig
                if isinstance(cfg, DropdownConfig):
                    choices = get_foreign_key_choices(model_field)
                    children_cfg[field_name] = replace(cfg, choices=choices)
        
        # Build action URL
        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name
        
        if instance is not None:
            action = reverse(f'bfe:{app_label}_{model_name}_update', args=[instance.pk])
        else:
            action = reverse(f'bfe:{app_label}_{model_name}_create')
        
        form_config = FormConfig(
            action=action,
            csrf=True,
            children=children_cfg,
            submit_text="Save" if instance else "Create",
        )
        
        # Pre-populate with instance data if editing
        initial = {}
        if instance is not None:
            for field_name in fields:
                if field_name not in self.exclude:
                    value = getattr(instance, field_name, None)
                    if hasattr(value, 'pk'):
                        initial[field_name] = str(value.pk)
                    elif value is not None:
                        initial[field_name] = str(value)
        
        return BFEFormWidget(
            config=form_config,
            request=request,
            data=request.POST or None,
            initial=initial,
        )
    
    def _resolve_layout(
        self,
        layout_config: WidgetConfig,
        instance: models.Model | None = None,
        readonly: bool = False,
    ) -> BFEBaseWidget:
        """
        Resolve a layout config, replacing field references with actual values.
        
        This handles SectionConfig/ColumnsConfig that reference field names
        and converts them to actual widget configs with values.
        """
        from ..builders import ChildBuilderRegistry
        from ..configs import LabelConfig
        from dataclasses import replace, fields as dataclass_fields
        
        # Check if this config has a 'fields' attribute (like SectionConfig)
        config_dict = {}
        has_fields_attr = hasattr(layout_config, 'fields') and layout_config.fields
        
        if has_fields_attr:
            # Convert field names to actual widget configs
            children_cfg = {}
            for field_name in layout_config.fields:
                if instance is not None:
                    value = getattr(instance, field_name, None)
                    display_value = str(value) if value is not None else "—"
                else:
                    display_value = ""
                
                model_field = self.model._meta.get_field(field_name)
                label = model_field.verbose_name.title() if hasattr(model_field, 'verbose_name') else field_name
                
                if readonly:
                    children_cfg[field_name] = LabelConfig(
                        name=field_name,
                        text=f"{label}: {display_value}",
                    )
                else:
                    # For forms, use the generated config
                    from .field_mapping import config_for_field
                    children_cfg[field_name] = config_for_field(model_field)
            
            # Merge with existing children
            if hasattr(layout_config, 'children') and layout_config.children:
                children_cfg.update(layout_config.children)
            
            # Create new config with resolved children
            config_dict['children'] = children_cfg
        
        # Handle nested columns (for ColumnsConfig)
        if hasattr(layout_config, 'columns') and layout_config.columns:
            resolved_columns = tuple(
                self._resolve_layout(col_cfg, instance, readonly).config
                for col_cfg in layout_config.columns
            )
            config_dict['columns'] = resolved_columns
        
        # Apply changes if any
        if config_dict:
            resolved_config = replace(layout_config, **config_dict)
        else:
            resolved_config = layout_config
        
        # Build the widget
        return ChildBuilderRegistry.build(resolved_config)

