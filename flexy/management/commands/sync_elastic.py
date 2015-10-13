from django.core.management.base import BaseCommand, CommandError
from ... import index


class Command(BaseCommand):

    help = 'Syncronizes elastic indexes'

    def add_arguments(self, parser):
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
            'updated': [],
            'created': []
        }
        for index_name, index_object in indexes.itervalues():
            if index_object.exists:
                index_object.update()
                status['updated'].append(index_name)
            else:
                index_object.create()
                status['created'].append(index_name)
        if len(status['created']) > 0:
            self.stdout.write('Successfully created indexes: {}'.format(
                ', '.join(status['created'])
            ))
        if len(status['updated']) > 0:
            self.stdout.write('Successfully updated indexes: {}'.format(
                ', '.join(status['updated'])
            ))
