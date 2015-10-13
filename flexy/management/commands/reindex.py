from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from ... import index
from ...handlers import get_index_data


class Command(BaseCommand):

    help = 'Index content into elastic'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true',
                            help="If set, cleans the index before reindexing")
        parser.add_argument('--start', type=int, default=0,
                            help="Starting offset")
        parser.add_argument('--limit', type=int, default=0,
                            help="How many items to process, all if unset")
        parser.add_argument('models', nargs='+', metavar='applabel.modelname')

    def handle(self, *args, **options):
        indexer_definitions = getattr(settings, 'FLEXY_INDEXERS')
        indexes = index.get_indexes()
        bulk_actions = {}
        for identifier in options['models']:
            Model = apps.get_model(identifier)
            objects = Model.objects.all()
            if options['limit'] != 0:
                objects = objects[
                    options['start']:(options['start']+options['limit'])
                ]
            else:
                objects = objects[options['start']:]
            for instance in objects:
                index_name, doc_type, id, data = get_index_data(
                    identifier,
                    instance,
                    indexes,
                    indexer_definitions
                )
                index_bulk_actions = bulk_actions.setdefault(index_name, [])
                index_bulk_actions.append(
                    {
                        'index': {
                            '_index': index_name,
                            '_type': doc_type,
                            '_id': id
                        }
                    }
                )
                index_bulk_actions.append(data)
        for index_name, index_bulk_actions in bulk_actions.iteritems():
            index_object = indexes[index_name]
            if options['clean']:
                if index_object.exists:
                    index_object.delete()
                    self.stdout.write('Deleted index {}'.format(index_name))
            if not index_object.exists:
                index_object.create()
                self.stdout.write('Created index {}'.format(index_name))
            index_object.connection.bulk(index_bulk_actions, refresh=True)
            self.stdout.write('Indexed {} items in index {}'.format(
                len(index_bulk_actions) / 2,
                index_name
            ))
