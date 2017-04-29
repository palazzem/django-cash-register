from django.apps import AppConfig
from django.conf import settings
from django.utils.module_loading import import_string


class RegistersConfig(AppConfig):
    name = 'registers'

    def ready(self):
        """
        Initializes all `registers` adapters after the application is loaded.
        """
        adapters_classes = [import_string(adapter) for adapter in settings.PUSH_ADAPTERS]
        settings.PUSH_ADAPTERS = [Adapter() for Adapter in adapters_classes]
