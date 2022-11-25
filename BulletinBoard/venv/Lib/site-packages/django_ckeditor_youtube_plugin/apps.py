"""
app config
"""

# Django
from django.apps import AppConfig

# Django CKEditor YouTube Plugin
from django_ckeditor_youtube_plugin import __version__


class CkeditorYouTubePluginConfig(AppConfig):
    """
    application config
    """

    name = "django_ckeditor_youtube_plugin"
    label = "django_ckeditor_youtube_plugin"
    verbose_name = f"Django CKEditor YouTube Plugin v{__version__}"
