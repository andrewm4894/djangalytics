from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.models import Project, Event
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generate sample analytics events for testing and demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of events to create (default: 100)'
        )
        parser.add_argument(
            '--project',
            type=str,
            help='Project slug to create events for (default: all active projects)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days back to spread events over (default: 7)'
        )

    def handle(self, *args, **options):
        count = options['count']
        project_slug = options['project']
        days_back = options['days']

        # Get target projects
        if project_slug:
            try:
                projects = [Project.objects.get(slug=project_slug, is_active=True)]
            except Project.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Project with slug "{project_slug}" not found')
                )
                return
        else:
            projects = Project.objects.filter(is_active=True)

        if not projects:
            self.stdout.write(self.style.WARNING('No active projects found'))
            return

        # Event types with realistic weights
        event_types = [
            ('page_view', 40),      # Most common
            ('button_click', 25),   # Common interactions
            ('app_start', 15),      # App launches
            ('search', 12),         # Search actions
            ('user_signup', 5),     # Less frequent but important
            ('purchase', 3),        # Conversion events
        ]

        # Expand event types based on weights
        weighted_events = []
        for event, weight in event_types:
            weighted_events.extend([event] * weight)

        sources = ['web', 'mobile', 'api', 'desktop']
        categories = ['marketing', 'product', 'support', 'sales']
        versions = ['1.0.0', '1.1.0', '1.2.0', '2.0.0']
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)',
            'Mozilla/5.0 (Android 11; Mobile; rv:92.0) Gecko/92.0',
        ]

        total_created = 0
        now = timezone.now()

        for project in projects:
            events_to_create = []
            
            self.stdout.write(f'Creating events for project: {project.name}')
            
            for i in range(count):
                # Random timestamp in specified days back, with more recent events weighted higher
                hours_ago = random.choices(
                    range(0, days_back * 24),
                    weights=[100 - (h // 4) for h in range(days_back * 24)]
                )[0]
                
                timestamp = now - timedelta(hours=hours_ago)
                
                event = Event(
                    project=project,
                    event_name=random.choice(weighted_events),
                    source=random.choice(sources),
                    timestamp=timestamp,
                    user_id=f'user_{random.randint(1, 50)}',
                    session_id=f'session_{random.randint(1, 20)}',
                    properties={
                        'value': random.randint(1, 1000),
                        'category': random.choice(categories),
                        'version': random.choice(versions),
                        'page': f'/page/{random.randint(1, 20)}',
                        'referrer': random.choice([
                            'google.com', 'direct', 'twitter.com', 'facebook.com'
                        ]),
                    },
                    user_agent=random.choice(user_agents),
                    ip_address=f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
                )
                events_to_create.append(event)

            # Bulk create for efficiency
            if events_to_create:
                Event.objects.bulk_create(events_to_create)
                total_created += len(events_to_create)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ Created {len(events_to_create)} events for {project.name}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully created {total_created} sample events across {len(projects)} projects'
            )
        )
        
        # Show summary
        self.stdout.write('\n📊 Event Summary:')
        for project in projects:
            event_count = Event.objects.filter(project=project).count()
            self.stdout.write(f'  {project.name}: {event_count} total events')