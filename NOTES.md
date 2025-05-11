Keep all *Config classes frozen. When you must tweak a single field, use:

my_cfg = dataclasses.replace(default_cfg, label="API key", required=True)

from byefrontend.configs.secret import SecretToggleConfig
from byefrontend.widgets import SecretToggleCharWidget

Widget creation today (works without touching other widgets):

cfg = SecretToggleConfig.build(
    name="api_secret",
    label="API secret",
    placeholder="********",
    is_in_form=True,
)
secret_widget = SecretToggleCharWidget(config=cfg)








########## NAVBAR
Boiler-plate explosion – every widget now needs a _create_data_json traversal. Consider a generic visitor that walks the widget tree once and lets each node append its payload – will keep the surface area in check.

Transition period – legacy call-sites still passing raw dicts will now fail with a TypeError. A quick win is to add a factory (NavBarConfig.from_legacy_dict) so downstream apps can migrate incrementally.

Selected-path UX – the positional list approach works, but it’s brittle if you reorder levels. A set of unique ids on each node plus lookup might age better.




########## BFEChildrenDict

A cleaner alternative

Because the widgets are now driven by frozen *Config objects you hardly ever need to mutate those mappings in-place. Two common patterns work better:

    Immutable children collection

from types import MappingProxyType
from dataclasses import replace

@dataclass(frozen=True, slots=True)
class WidgetConfig:
    ...
    children: Mapping[str, "WidgetConfig"] = field(default_factory=dict)

# When you “change” children you build a *new* config:
new_cfg = replace(old_cfg, children={**old_cfg.children, "extra": extra_child})
widget = Widget(config=new_cfg)

Pros: thread-safe, no cache-invalidation bookkeeping at all – a new object ⇒ new cache key.
Cons: requires functional style (“create-new-object”) everywhere, but that’s exactly the direction you are already going.

Explicit mutator API with a private dict

Keep an internal mutable dict but never expose it directly:

    class Widget(BFEBaseWidget):
        ...
        def add_child(self, key, child):
            self._children[key] = child
            self._invalidate_cache()

    Where _invalidate_cache() toggles the two flags and, optionally, propagates to the parent.
    This removes the need for a proxy subclass and makes mutation sites explicit.

My recommendation

Given that you’re leaning into immutable configs everywhere else, option 1 is the most coherent:

    Drop BFEChildrenDict.

    Treat attrs and children as read-only mappings (wrap them in MappingProxyType if you want runtime safety).

    When something “changes”, build a new config + new widget. That makes caching trivial (cache key = hash of the config) and eliminates a whole class of edge cases where caches aren’t invalidated correctly.

If you still have legacy call-sites that rely on mutation, add an explicit, well-documented helper (option 2) so that the invalidation logic is in one place – not scattered across half-overridden dict methods.

Either way you end up with less magic and a clearer mental model than the current BFEChildrenDict proxy.




csrf exempt makes no sense since upload js already fetches the token
















2. Security of the crypto helpers

Big 👍 for using XChaCha20-Poly1305 + Argon2. A few tweaks would harden things further:

    Key rotations & audit trail
    You already model EncryptedUnlockKey.is_active; consider adding rotated_at and a log of who triggered the rotation.

    Explicit version bytes
    Prepend a single version byte to every ciphertext (b'\x01' + nonce + ciphertext) so you can seamlessly migrate algorithms later.

    Authenticated context
    Right now aad defaults to empty. Inject something that binds the ciphertext to the DB row—e.g. str(self.pk).encode()—to kill accidental key/row swaps.

    Password strength enforcement
    Your Argon2 parameters are solid, but nothing stops a 3-character password. Hook in Django’s built-in validators (they’re already listed under AUTH_PASSWORD_VALIDATORS, just apply them when you call set_key()).














3. Front-end widgets architecture

    The immutable-config pattern (@dataclass(frozen=True) + replace) is a breath of fresh air compared to the mutable, side-effect-prone widget APIs we see in many Django libraries.
    Opinion: I’d surface those convenience tweak() helpers in the docs right away—people will love them.

    Caching toggles
    BFEBaseWidget.render() and .media honour a settings.BFE_WIDGET_CACHE flag but the “backend” isn’t implemented yet. Either ship a dead-simple in-memory LRU or remove the flag until ready; half-wired cache flags bite later.

    BFEChildrenDict recursion triggers
    Be wary of the blanket setattr(..., True) in mark_parent_for_recache(). If any code writes to a cache-relevant attr inside a property setter, you could end up in a loop. I couldn’t spot an immediate offender, but unit-test that path.

    JS driver vs server-side render
    The navbar renders a single empty <nav> and offloads everything to navbar.js. That’s great for dynamic UX, but hurts SEO/accessibility. Consider a graceful degradation path (server-render first, hydrate if JS present).



   


   
Page() object



SiteStructure() object?



Carousel
DropDown
AnimatedBackground(based on scroll, mouse position, time)
VideoPlayer
AudioPlayer
Map
