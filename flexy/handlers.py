from collections import Mapping
from django.conf import settings
from django.utils import module_loading
from django.dispatch import receiver
from django.db.models import signals

from . import index


def model_identifier(Klass):
    return '{}.{}'.format(
        Klass._meta.app_label,
        Klass._meta.model_name
    )


def _coalesce(value_or_callable):
    if callable(value_or_callable):
        return value_or_callable()
    return value_or_callable


def get_index_data(identifier, instance, indexes, indexer_definitions):
    index_definition = indexer_definitions[identifier]
    results = []
    if isinstance(index_definition, Mapping):
        index_name = index_definition['index']
        doc_type = index_definition['type']
        data = {
            k: _coalesce(getattr(instance, v)) for k, v in
            index_definition['data'].iteritems()
        }
        id = '{}:{}'.format(identifier, instance.pk)
        results.append(
            (index_name, doc_type, id, data)
        )
    else:
        index_definition_generator = module_loading.import_string(
            index_definition
        )
        for index_definition in index_definition_generator(instance):
            index_name = index_definition['index']
            doc_type = index_definition['type']
            data = index_definition['data']
            id = index_definition.get('id')
            if id is None:
                id = '{}:{}'.format(identifier, instance.pk)
            results.append(
                (index_name, doc_type, id, data)
            )
    return results


def index_object(identifier, instance, indexes, indexer_definitions):
    for (index_name, doc_type, id, data) in get_index_data(
        identifier,
        instance,
        indexes,
        indexer_definitions
    ):
        indexes[index_name].index(
            doc_type,
            id,
            data
        )


@receiver(signals.post_save)
def index_content(sender, **kwargs):
    indexer_definitions = getattr(settings, 'FLEXY_INDEXERS')
    identifier = model_identifier(sender)
    if not kwargs.get('raw', False) and identifier in indexer_definitions:
        indexes = index.get_indexes()
        instance = kwargs['instance']
        index_object(identifier, instance, indexes, indexer_definitions)


@receiver(signals.post_delete)
def remove_content(sender, **kwargs):
    indexer_definitions = getattr(settings, 'FLEXY_INDEXERS')
    identifier = model_identifier(sender)
    if identifier in indexer_definitions:
        indexes = index.get_indexes()
        instance = kwargs['instance']
        for (index_name, doc_type, id, __) in get_index_data(
            identifier,
            instance,
            indexes,
            indexer_definitions
        ):
            indexes[index_name].unindex(
                doc_type,
                id
            )
