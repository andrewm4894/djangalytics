from django.core.management.base import BaseCommand
from analytics.models import Project


class Command(BaseCommand):
    help = 'Set up default projects for the demo'

    def handle(self, *args, **options):
        # Create or update projects
        projects_config = [
            {
                'name': 'Default Dashboard',
                'slug': 'default',
                'api_key': 'pk_PNJYbjX44sGzb6DoeqDAgpoYlPGNyJJs8yEkeP1_3so',
                'allowed_sources': ['web', 'frontend-dashboard'],
                'rate_limit_per_minute': 1000,
            },
            {
                'name': 'Snake Game',
                'slug': 'snake-game',
                'api_key': 'pk_snake_demo_key_12345678901234567890123',
                'allowed_sources': ['snake-game', 'web'],
                'rate_limit_per_minute': 2000,
            },
            {
                'name': 'Flappy Hedgehog',
                'slug': 'flappy-hedgehog', 
                'api_key': 'pk_flappy_demo_key_12345678901234567890123',
                'allowed_sources': ['flappy-hedgehog', 'web'],
                'rate_limit_per_minute': 2000,
            }
        ]

        for config in projects_config:
            project, created = Project.objects.get_or_create(
                slug=config['slug'],
                defaults={
                    'name': config['name'],
                    'api_key': config['api_key'],
                    'allowed_sources': config['allowed_sources'],
                    'rate_limit_per_minute': config['rate_limit_per_minute'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created project: {project.name} (API key: {project.api_key})')
                )
            else:
                # Update existing project
                project.name = config['name']
                project.api_key = config['api_key']
                project.allowed_sources = config['allowed_sources']
                project.rate_limit_per_minute = config['rate_limit_per_minute']
                project.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated existing project: {project.name}')
                )

        self.stdout.write(self.style.SUCCESS('Project setup complete!'))