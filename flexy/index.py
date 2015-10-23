from django.conf import settings
from elasticsearch_dsl import index


class Index(object):

    def __init__(self, slug, settings, mappings, connection='default'):
        self.wrapped = index.Index(
            slug,
            using=connection
        )
        if settings:
            self.wrapped.settings(**settings)
        self.mappings = None
        if mappings:
            self.mappings = mappings

    def put_mappings(self):
        if self.mappings is not None:
            for mapping_name, mapping_data in self.mappings.iteritems():
                self.connection.indices.put_mapping(
                    index=self.wrapped._name,
                    doc_type=mapping_name,
                    body=mapping_data
                )

    def create(self):
        if not self.exists:
            self.wrapped.create()
            self.put_mappings()

    def delete(self):
        if self.exists:
            self.wrapped.delete()

    def update(self):
        if self.exists:
            kwargs = self.wrapped.to_dict()
            if kwargs.get('settings'):
                self.connection.indices.put_settings(
                    index=self.wrapped._name,
                    body=kwargs['settings']
                )
            self.put_mappings()

    @property
    def connection(self):
        return self.wrapped.connection

    @property
    def exists(self):
        return self.connection.indices.exists(self.wrapped._name)

    def index(self, doc_type, id, data, refresh=True):
        self.connection.index(
            index=self.wrapped._name,
            doc_type=doc_type,
            id=id,
            body=data,
            refresh=refresh
        )

    def unindex(self, doc_type, id, refresh=True):
        self.connection.delete(
            index=self.wrapped._name,
            doc_type=doc_type,
            id=id,
            refresh=refresh
        )


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
