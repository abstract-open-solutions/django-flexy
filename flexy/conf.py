from django.conf import settings  # NOQA
from appconf import AppConf


class FlexyAppConf(AppConf):

    CONNECTIONS = {
        'default': {
            'hosts': 'elastic'
        }
    }

    INDEXES = {
        'main': {}
    }

    INDEXERS = {}

    class Meta:
        prefix = 'flexy'
