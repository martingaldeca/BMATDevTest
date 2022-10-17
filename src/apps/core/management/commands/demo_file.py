import os
import random
import string
import datetime

from django.core.management.base import BaseCommand
from factory import fuzzy


class Command(BaseCommand):

    help = (
        'Create demo data for the dev test.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--total_size',
            type=int,
            default=1_000_000_000,  # Default 1GB
            help='Total size of the file in Bytes'
        )
        parser.add_argument(
            '-n',
            '--file_name',
            type=str,
            default='test_data.csv',
            help='File name',
        )

    def handle(self, *args, **options):
        total_size = options['total_size']
        file_name = options['file_name']
        counter = 0
        with open(f'apps/data_processor/csvs/in/{file_name}', 'a') as file_object:
            print('0 entries added to file...')
            file_object.write('Song,Date,Number of Plays\n')
            while os.path.getsize(f'apps/data_processor/csvs/in/{file_name}') < total_size:

                # Only 5 letters in order to repeat values
                song_name = ''.join(random.choice(string.ascii_lowercase) for i in range(4))
                date = fuzzy.FuzzyDate(datetime.date(1994, 8, 8)).fuzz().isoformat()
                song_plays = random.randint(1, 100000)
                file_object.write(f'{song_name},{date},{song_plays}\n')
                counter += 1

                if counter % 100000 == 0:
                    percentage = round(
                        (os.path.getsize(f'apps/data_processor/csvs/in/{file_name}') / total_size) * 100, 2
                    )
                    print(
                        f'{percentage} % '
                        f'{counter} entries added to file...'
                    )
