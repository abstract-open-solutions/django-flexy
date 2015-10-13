from django.apps import apps


def load_instance(elastic_result):
    """Loads a django model instance given a result.
    """
    model_identifier, primary_key = elastic_result.meta.id.split(':', 1)
    Model = apps.get_model(model_identifier)
    return Model.objects.get(pk=primary_key)


def load_instances(elastic_results):
    """Same as ``load_instance``, working efficiently on any iterable.

    It's not super efficient, it just minimizes
    the queries that hit the database.
    """
    instances_mappings = {}
    instances_to_load = {}
    instances = {}
    # Determines models and pks to load
    for index, elastic_result in enumerate(elastic_results):
        model_identifier, primary_key = elastic_result.meta.id.split(':', 1)
        instances_mappings[(model_identifier, primary_key)] = index
        instances_to_load.setdefault(model_identifier, []).append(primary_key)
    # Loads them
    for model_identifier, pks in instances_to_load.iteritems():
        Model = apps.get_model(model_identifier)
        for instance in Model.objects.get(pk__in=pks):
            position = instances_mappings[(model_identifier, instance.pk)]
            instances[position] = instance
    # Interleaves and keeps ordering
    return [
        instances[i] for i in xrange(0, len(elastic_results))
    ]
