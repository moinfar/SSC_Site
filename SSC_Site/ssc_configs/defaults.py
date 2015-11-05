from mezzanine.conf import register_setting
from django.utils.translation import ugettext_lazy as _

register_setting(
    name="FIRST_PAGE_PARALLAX",
    label=_("Parallax of index page"),
    description="Url of an image that is shown in the first page as parallax.",
    editable=True,
    default="https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
)

# accessible in templates.
register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    description=_("Sequence of setting names available within templates."),
    editable=False,
    default=("FIRST_PAGE_PARALLAX",),
    append=True,
)

