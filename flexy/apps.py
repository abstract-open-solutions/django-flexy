from django.apps import AppConfig

from . import connections


class FlexyConfig(AppConfig):

    name = 'flexy'
    verbose_name = "Flexy (Elasticsearch integration)"

    def ready(self):
        # Configure connections
        connections.configure()
