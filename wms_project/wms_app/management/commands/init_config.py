from django.core.management.base import BaseCommand
from wms_app.models import BaseMap, ArcGISConfig


class Command(BaseCommand):
    help = 'Initialize default configuration data'

    def handle(self, *args, **options):
        # Create default basemaps
        default_basemaps = [
            {
                'service_type': 'OSM',
                'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'attribution': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                'subdomains': ['a', 'b', 'c']
            },
            {
                'service_type': 'SATELLITE',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                'attribution': 'Tiles © Esri',
                'subdomains': None
            }
        ]

        for basemap_data in default_basemaps:
            basemap, created = BaseMap.objects.get_or_create(
                service_type=basemap_data['service_type'],
                defaults={
                    'url': basemap_data['url'],
                    'attribution': basemap_data['attribution'],
                    'subdomains': basemap_data['subdomains']
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created basemap: {basemap.service_type}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Basemap already exists: {basemap.service_type}')
                )

        # Create default ArcGIS config
        arcgis_config, created = ArcGISConfig.objects.get_or_create(
            defaults={
                'portal_url': 'https://gissoft.esrivn.net/portal',
                'api_url': 'https://gissoft.esrivn.net/server/rest/services'
            }
        )
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created ArcGIS configuration')
            )
        else:
            self.stdout.write(
                self.style.WARNING('ArcGIS configuration already exists')
            )

        self.stdout.write(
            self.style.SUCCESS('Configuration initialization completed successfully!')
        )
