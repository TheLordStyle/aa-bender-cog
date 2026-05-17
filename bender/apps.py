from django.apps import AppConfig

from bender import __version__


class BenderConfig(AppConfig):
    name = "bender"
    label = "bender"
    verbose_name = f"Bender Cog v{__version__}"
