from django.test import TestCase

from .widgets import BFEFormWidget
from .configs import FormConfig, TagInputConfig


class TagInputWidgetTests(TestCase):
    def test_cleaned_data_is_list_of_tags(self):
        cfg = FormConfig(children={"tags": TagInputConfig()})
        form = BFEFormWidget(config=cfg, data={"tags": "one,two, three"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["tags"], ["one", "two", "three"])


