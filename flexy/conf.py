from django.conf import settings  # NOQA
from appconf import AppConf


class FlexyAppConf(AppConf):

    CONNECTIONS = {
        'default': {
            'hosts': 'elastic'
        }
    }

    INDEXES = {
        'main': {
            'connection': 'default',
            'settings': {},
            'mappings': {}
        }
    }

    MODELS = {}
    # MODELS = {
    #     'appname.foo': {
    #         '_index': 'main',
    #         '_type': 'foo',
    #         '_id': 'fieldname',
    #         'field': 'fieldname'
    #     },
    #     'appname.bar': 'appname.indexers.bar'
    # }

    class Meta:
        prefix = 'flexy'
