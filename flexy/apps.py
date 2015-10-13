from django.apps import AppConfig


class FlexyConfig(AppConfig):

    name = 'flexy'
    verbose_name = "Flexy (Elasticsearch integration)"

    def ready(self):
        # Configure and hook up elastic stuff
        pass
