import json
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь до JSON файла.')

    def handle(self, *args, **options):
        json_file = options['json_file']
        absolute_path = os.path.abspath(json_file)
        self.stdout.write(f'Parsing JSON file: {absolute_path}')

        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        objects_to_create = [
            Ingredient(name=item['name'],
                       measurement_unit=item['measurement_unit'])
            for item in data
        ]
        Ingredient.objects.bulk_create(objects_to_create)
        self.stdout.write(self.style.SUCCESS('Данные загружены в БД.'))
