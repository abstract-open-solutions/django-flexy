from django.conf import settings
from elasticsearch_dsl import connections
from elasticsearch_dsl import index


class Index(object):

    def __init__(self, slug, settings, mappings, connection='default'):
        self.wrapped = index.Index(
            slug,
            using=connection
        )
        self.kwargs = {}
        if settings:
            self.kwargs['settings'] = settings
        if mappings:
            self.kwargs['mappings'] = mappings

    def create(self):
        if not self.exists:
            self.wrapped.create(**self.kwargs)

    def delete(self):
        if self.exists:
            self.wrapped.delete()

    def update(self):
        self.wrapped.connection.indices.put_settings(
            index=self.wrapped._name,
            body=self.kwargs['settings']
        )
        for mapping_name, mapping_data in self.kwargs['mappings'].iteritems():
            self.wrapped.connection.indices.put_mapping(
                index=self.wrapped._name,
                doc_type=mapping_name,
                body=mapping_data
            )

    @property
    def exists(self):
        return self.wrapped.connection.indices.exists(
            self.wrapped._name
        )


def configure():
    connections_definitions = getattr(settings, 'FLEXY_CONNECTIONS', {})
    connections.configure(**connections_definitions)


def get_indexes():
    definitions = getattr(settings, 'FLEXY_INDEXES', {})
    indexes = {}
    for slug, data in definitions.iteritems():
        indexes[slug] = Index(
            slug,
            data.get('settings', {}),
            data.get('mappings', {}),
            data.get('connection', 'default')
        )
    return indexes
