from django.core.management.base import BaseCommand, CommandError
from ... import index


class Command(BaseCommand):

    help = 'Deletes elastic indexes, optionally recreating them'

    def add_arguments(self, parser):
        parser.add_argument('--recreate', action='store_true',
                            help='recereates indexes after deletion')
        parser.add_argument('indexes', nargs='*', metavar='index',
                            help='Index identifier')

    def handle(self, *args, **options):
        indexes = index.get_indexes()
        if options['indexes']:
            filtered_indexes = {}
            for index_name in options['indexes']:
                if index_name not in indexes:
                    raise CommandError(
                        "Index '{}' is not present".format(index_name)
                    )
                filtered_indexes[index_name] = indexes[index_name]
            indexes = filtered_indexes
        status = {
            'deleted': [],
            'created': []
        }
        for index_name, index_object in indexes.iteritems():
            if index_object.exists:
                index_object.delete()
                status['deleted'].append(index_name)
        if options['recreate']:
            for index_name in status['deleted']:
                indexes[index_name].create()
                status['created'].append(index_name)
        if len(status['deleted']) > 0:
            self.stdout.write('Successfully deleted indexes: {}'.format(
                ', '.join(status['deleted'])
            ))
        if len(status['created']) > 0:
            self.stdout.write('Successfully recreated indexes: {}'.format(
                ', '.join(status['created'])
            ))
