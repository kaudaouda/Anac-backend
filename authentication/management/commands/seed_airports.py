from django.core.management.base import BaseCommand
from authentication.models import Airport
from decimal import Decimal


class Command(BaseCommand):
    help = 'Peupler la base de données avec les aéroports et aérodromes de la Côte d\'Ivoire'

    def handle(self, *args, **options):
        self.stdout.write('Début du peuplement des aéroports et aérodromes...')
        
        airports_data = [
            {
                'airport_id': 'abj',
                'name': 'Aéroport Félix Houphouët-Boigny',
                'code': 'ABJ',
                'airport_type': 'international',
                'city': 'Abidjan',
                'latitude': Decimal('5.2614'),
                'longitude': Decimal('-3.9258'),
                'radius': Decimal('8.0'),
                'description': 'Principal aéroport international de la Côte d\'Ivoire'
            },
            {
                'airport_id': 'bqu',
                'name': 'Aéroport de Bouaké',
                'code': 'BQU',
                'airport_type': 'domestic',
                'city': 'Bouaké',
                'latitude': Decimal('7.7389'),
                'longitude': Decimal('-5.0736'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Bouaké'
            },
            {
                'airport_id': 'bvg',
                'name': 'Aéroport de Boundiali',
                'code': 'BVG',
                'airport_type': 'domestic',
                'city': 'Boundiali',
                'latitude': Decimal('9.5333'),
                'longitude': Decimal('-6.4667'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Boundiali'
            },
            {
                'airport_id': 'djo',
                'name': 'Aéroport de Daloa',
                'code': 'DJO',
                'airport_type': 'domestic',
                'city': 'Daloa',
                'latitude': Decimal('6.7928'),
                'longitude': Decimal('-6.4733'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Daloa'
            },
            {
                'airport_id': 'gox',
                'name': 'Aéroport de Gagnoa',
                'code': 'GOX',
                'airport_type': 'domestic',
                'city': 'Gagnoa',
                'latitude': Decimal('6.1333'),
                'longitude': Decimal('-5.9333'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Gagnoa'
            },
            {
                'airport_id': 'kgo',
                'name': 'Aéroport de Korhogo',
                'code': 'KGO',
                'airport_type': 'domestic',
                'city': 'Korhogo',
                'latitude': Decimal('9.4167'),
                'longitude': Decimal('-5.6167'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Korhogo'
            },
            {
                'airport_id': 'mjc',
                'name': 'Aéroport de Man',
                'code': 'MJC',
                'airport_type': 'domestic',
                'city': 'Man',
                'latitude': Decimal('7.2721'),
                'longitude': Decimal('-7.5874'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Man'
            },
            {
                'airport_id': 'ody',
                'name': 'Aéroport d\'Odienné',
                'code': 'ODY',
                'airport_type': 'domestic',
                'city': 'Odienné',
                'latitude': Decimal('9.5000'),
                'longitude': Decimal('-7.5667'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique d\'Odienné'
            },
            {
                'airport_id': 'sik',
                'name': 'Aéroport de San-Pédro',
                'code': 'SIK',
                'airport_type': 'domestic',
                'city': 'San-Pédro',
                'latitude': Decimal('4.7467'),
                'longitude': Decimal('-6.6608'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de San-Pédro'
            },
            {
                'airport_id': 'tou',
                'name': 'Aéroport de Touba',
                'code': 'TOU',
                'airport_type': 'domestic',
                'city': 'Touba',
                'latitude': Decimal('8.2833'),
                'longitude': Decimal('-7.6833'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Touba'
            },
            {
                'airport_id': 'yab',
                'name': 'Aéroport de Yamoussoukro',
                'code': 'YAB',
                'airport_type': 'domestic',
                'city': 'Yamoussoukro',
                'latitude': Decimal('6.9031'),
                'longitude': Decimal('-5.3656'),
                'radius': Decimal('5.0'),
                'description': 'Aéroport domestique de Yamoussoukro'
            }
        ]
        
        # Données des aérodromes
        aerodromes_data = [
            {
                'airport_id': 'adz-1',
                'name': 'Aérodrome d\'Adzopé',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Adzopé',
                'latitude': Decimal('6.1167'),
                'longitude': Decimal('-3.8667'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil d\'Adzopé'
            },
            {
                'airport_id': 'agn-1',
                'name': 'Aérodrome d\'Agboville',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Agboville',
                'latitude': Decimal('5.9333'),
                'longitude': Decimal('-4.2167'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil d\'Agboville'
            },
            {
                'airport_id': 'bdi-1',
                'name': 'Aérodrome de Bondoukou',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Bondoukou',
                'latitude': Decimal('8.0333'),
                'longitude': Decimal('-2.8000'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Bondoukou'
            },
            {
                'airport_id': 'bng-1',
                'name': 'Aérodrome de Bangolo',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Bangolo',
                'latitude': Decimal('7.0167'),
                'longitude': Decimal('-7.4833'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Bangolo'
            },
            {
                'airport_id': 'dab-1',
                'name': 'Aérodrome de Dabou',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Dabou',
                'latitude': Decimal('5.3167'),
                'longitude': Decimal('-4.3833'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Dabou'
            },
            {
                'airport_id': 'gbl-1',
                'name': 'Aérodrome de Grand-Bassam',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Grand-Bassam',
                'latitude': Decimal('5.2000'),
                'longitude': Decimal('-3.7333'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Grand-Bassam'
            },
            {
                'airport_id': 'iss-1',
                'name': 'Aérodrome d\'Issia',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Issia',
                'latitude': Decimal('6.4833'),
                'longitude': Decimal('-6.5833'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil d\'Issia'
            },
            {
                'airport_id': 'kat-1',
                'name': 'Aérodrome de Katiola',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Katiola',
                'latitude': Decimal('8.1333'),
                'longitude': Decimal('-5.1000'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Katiola'
            },
            {
                'airport_id': 'seg-1',
                'name': 'Aérodrome de Séguéla',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Séguéla',
                'latitude': Decimal('7.9667'),
                'longitude': Decimal('-6.6667'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Séguéla'
            },
            {
                'airport_id': 'tab-1',
                'name': 'Aérodrome de Tabou',
                'code': '',
                'airport_type': 'aerodrome',
                'city': 'Tabou',
                'latitude': Decimal('4.4167'),
                'longitude': Decimal('-7.3500'),
                'radius': Decimal('3.0'),
                'description': 'Aérodrome civil de Tabou'
            }
        ]
        
        # Combiner toutes les données
        all_data = airports_data + aerodromes_data
        
        created_count = 0
        updated_count = 0
        
        for data in all_data:
            airport, created = Airport.objects.update_or_create(
                airport_id=data['airport_id'],
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ Créé: {airport.name}')
            else:
                updated_count += 1
                self.stdout.write(f'✓ Mis à jour: {airport.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nPeuplement terminé ! {created_count} créés, {updated_count} mis à jour.'
            )
        )
