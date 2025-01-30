from django.core.management import BaseCommand

from PeopleFind.celery import app as celery_app

class Command(BaseCommand):
    help = 'Run Celery worker with specified options.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p', '--pool',
            choices=['solo', 'threads', 'processes'],
            default='solo',
            help='Pool implementation to use.',
        )
        parser.add_argument(
            '-l', '--loglevel',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            default='INFO',
            help='Logging level.',
        )

    def handle(self, *args, **options):
        pool = options['pool']
        loglevel = options['loglevel'].lower()

        argv = [
            'worker',
            f'--loglevel={loglevel}',
            f'--pool={pool}',
            f'-E'
        ]

        self.stdout.write(f'Starting Celery worker with pool "{pool}" and loglevel "{loglevel}".')
        celery_app.worker_main(argv)
