from mezzanine.conf import register_setting
from django.utils.translation import ugettext_lazy as _

register_setting(
    name="SCREEN_LEFT",
    label=_("Label of left monitor page"),
    description="Label of left monitor page that is shown in index page.",
    editable=True,
    default="uni",
)

register_setting(
    name="SCREEN_RIGHT",
    label=_("Label of right monitor page"),
    description="Label of right monitor page that is shown in index page.",
    editable=True,
    default="ssc",
)

# accessible in templates.
register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    description=_("Sequence of setting names available within templates."),
    editable=False,
    default=("SCREEN_LEFT", "SCREEN_RIGHT"),
    append=True,
)

