"""
Example BFE Model Views for the template app.

This demonstrates how to use the BFEModelView system to
automatically generate views for Django models.
"""
from byefrontend.model_views import bfe, BFEModelView
from byefrontend.configs import SectionConfig, ColumnsConfig, TextInputConfig

from .models import Feedback, DataForFiltering


@bfe.register(Feedback)
class FeedbackView(BFEModelView):
    """
    View configuration for the Feedback model.
    
    Demonstrates basic list/detail/form views.
    """
    # List view: show these columns
    list_fields = ('name', 'email', 'created')
    list_per_page = 20
    
    # Detail view: custom layout with sections
    detail_layout = SectionConfig(
        title="Feedback Details",
        fields=('name', 'email', 'message', 'created'),
        bordered=True,
        padded=True,
    )
    
    # Form view: use default auto-generated form
    form_fields = ('name', 'email', 'message')


@bfe.register(DataForFiltering)
class DataForFilteringView(BFEModelView):
    """
    View configuration for the DataForFiltering model.
    
    Demonstrates filters, search, and multi-column layouts.
    """
    # List view with filters and search
    list_fields = ('name', 'domain', 'is_active', 'account_credits', 'created')
    list_filters = ('is_active',)
    list_search_fields = ('name', 'domain')
    list_per_page = 25
    
    # Detail view: two-column layout
    detail_layout = ColumnsConfig(
        columns=(
            SectionConfig(
                title="Identity",
                fields=('name', 'domain', 'birthday'),
                collapsible=False,
            ),
            SectionConfig(
                title="Status & Credits",
                fields=('is_active', 'is_admin', 'account_credits'),
                collapsible=False,
            ),
        ),
        ratios=(1, 1),
        gap=1.5,
    )
    
    # Form view: exclude auto-fields
    form_fields = ('name', 'domain', 'birthday', 'is_active', 'is_admin', 'account_credits')

