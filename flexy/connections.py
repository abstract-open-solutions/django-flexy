from django.conf import settings
from elasticsearch_dsl.connections import connections


def configure():
    connections_definitions = getattr(settings, 'FLEXY_CONNECTIONS', {})
    connections.configure(**connections_definitions)
