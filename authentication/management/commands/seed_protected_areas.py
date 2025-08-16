from django.core.management.base import BaseCommand
from authentication.models import NaturalReserve, NationalPark, ProtectedAreaCoordinates
from decimal import Decimal


class Command(BaseCommand):
    help = 'Peupler la base de données avec les réserves naturelles et parcs nationaux de la Côte d\'Ivoire'

    def handle(self, *args, **options):
        self.stdout.write('Début du peuplement des zones protégées...')
        
        # Données des réserves naturelles
        natural_reserves_data = [
            {
                'reserve_id': 'res-comoe',
                'name': 'Réserve Naturelle de la Comoé',
                'area': '11,500 km²',
                'description': 'Plus grande réserve naturelle d\'Afrique de l\'Ouest',
                'coordinates': [
                    [5.2000, -3.8000],
                    [5.6000, -3.7500],
                    [5.9000, -3.6000],
                    [6.1000, -3.4000],
                    [6.0000, -3.2000],
                    [5.7000, -3.1000],
                    [5.4000, -3.2000],
                    [5.2000, -3.4000],
                    [5.1000, -3.6000],
                    [5.2000, -3.8000]
                ]
            },
            {
                'reserve_id': 'res-tai',
                'name': 'Réserve Naturelle de Taï',
                'area': '3,300 km²',
                'description': 'Réserve de forêt tropicale primaire',
                'coordinates': [
                    [5.2000, -7.7000],
                    [5.5000, -7.6000],
                    [5.8000, -7.5000],
                    [5.9000, -7.3000],
                    [5.8000, -7.1000],
                    [5.5000, -7.2000],
                    [5.2000, -7.3000],
                    [5.1000, -7.5000],
                    [5.2000, -7.7000]
                ]
            },
            {
                'reserve_id': 'res-azagny',
                'name': 'Réserve Naturelle d\'Azagny',
                'area': '194 km²',
                'description': 'Réserve côtière avec mangroves et lagunes',
                'coordinates': [
                    [5.0000, -4.9000],
                    [5.3000, -4.8000],
                    [5.4000, -4.6000],
                    [5.3000, -4.4000],
                    [5.1000, -4.3000],
                    [4.9000, -4.4000],
                    [4.8000, -4.6000],
                    [4.9000, -4.8000],
                    [5.0000, -4.9000]
                ]
            },
            {
                'reserve_id': 'res-niokolo',
                'name': 'Réserve Naturelle du Niokolo-Koba',
                'area': '9,130 km²',
                'description': 'Réserve de savane et forêt galerie',
                'coordinates': [
                    [8.0000, -7.5000],
                    [8.3000, -7.4000],
                    [8.6000, -7.3000],
                    [8.8000, -7.1000],
                    [8.7000, -6.9000],
                    [8.4000, -6.8000],
                    [8.1000, -6.9000],
                    [7.9000, -7.1000],
                    [8.0000, -7.5000]
                ]
            }
        ]
        
        # Données des parcs nationaux
        national_parks_data = [
            {
                'park_id': 'parc-comoe',
                'name': 'Parc National de la Comoé',
                'area': '11,500 km²',
                'description': 'Parc national classé au patrimoine mondial de l\'UNESCO',
                'coordinates': [
                    [8.0000, -3.5000],
                    [8.4000, -3.4000],
                    [8.7000, -3.2000],
                    [8.9000, -3.0000],
                    [8.8000, -2.8000],
                    [8.5000, -2.7000],
                    [8.2000, -2.8000],
                    [8.0000, -3.0000],
                    [7.9000, -3.2000],
                    [8.0000, -3.5000]
                ]
            },
            {
                'park_id': 'parc-tai',
                'name': 'Parc National de Taï',
                'area': '3,300 km²',
                'description': 'Parc national de forêt tropicale humide',
                'coordinates': [
                    [5.2000, -7.7000],
                    [5.6000, -7.6000],
                    [5.9000, -7.4000],
                    [6.0000, -7.2000],
                    [5.9000, -7.0000],
                    [5.6000, -7.1000],
                    [5.3000, -7.2000],
                    [5.2000, -7.4000],
                    [5.1000, -7.6000],
                    [5.2000, -7.7000]
                ]
            },
            {
                'park_id': 'parc-maroua',
                'name': 'Parc National de Marahoué',
                'area': '1,010 km²',
                'description': 'Parc national de forêt dense humide',
                'coordinates': [
                    [6.5000, -6.5000],
                    [6.8000, -6.4000],
                    [7.1000, -6.3000],
                    [7.2000, -6.1000],
                    [7.1000, -5.9000],
                    [6.8000, -6.0000],
                    [6.5000, -6.1000],
                    [6.4000, -6.3000],
                    [6.5000, -6.5000]
                ]
            },
            {
                'park_id': 'parc-azagny',
                'name': 'Parc National d\'Azagny',
                'area': '194 km²',
                'description': 'Parc national côtier et maritime',
                'coordinates': [
                    [5.0000, -4.9000],
                    [5.2000, -4.8000],
                    [5.4000, -4.6000],
                    [5.3000, -4.4000],
                    [5.1000, -4.3000],
                    [4.9000, -4.4000],
                    [4.8000, -4.6000],
                    [4.9000, -4.8000],
                    [5.0000, -4.9000]
                ]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        # Créer les réserves naturelles
        for reserve_data in natural_reserves_data:
            coordinates = reserve_data.pop('coordinates')
            reserve, created = NaturalReserve.objects.update_or_create(
                reserve_id=reserve_data['reserve_id'],
                defaults=reserve_data
            )
            
            # Créer les coordonnées
            ProtectedAreaCoordinates.objects.filter(natural_reserve=reserve).delete()
            for i, coord in enumerate(coordinates):
                ProtectedAreaCoordinates.objects.create(
                    natural_reserve=reserve,
                    latitude=Decimal(str(coord[0])),
                    longitude=Decimal(str(coord[1])),
                    order=i
                )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ Créée: {reserve.name}')
            else:
                updated_count += 1
                self.stdout.write(f'✓ Mise à jour: {reserve.name}')
        
        # Créer les parcs nationaux
        for park_data in national_parks_data:
            coordinates = park_data.pop('coordinates')
            park, created = NationalPark.objects.update_or_create(
                park_id=park_data['park_id'],
                defaults=park_data
            )
            
            # Créer les coordonnées
            ProtectedAreaCoordinates.objects.filter(national_park=park).delete()
            for i, coord in enumerate(coordinates):
                ProtectedAreaCoordinates.objects.create(
                    national_park=park,
                    latitude=Decimal(str(coord[0])),
                    longitude=Decimal(str(coord[1])),
                    order=i
                )
            
            if created:
                created_count += 1
                self.stdout.write(f'✓ Créé: {park.name}')
            else:
                updated_count += 1
                self.stdout.write(f'✓ Mis à jour: {park.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nPeuplement terminé ! {created_count} créés, {updated_count} mis à jour.'
            )
        )
