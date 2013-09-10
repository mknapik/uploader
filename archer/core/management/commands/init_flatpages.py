from django.core.management.base import BaseCommand, CommandError
from django.contrib.flatpages.models import FlatPage, Site
from archer.settings.common import get_host_name


class Command(BaseCommand):
    args = '[domain]'
    help = 'initialize static pages like "Getting Started"'

    def handle(self, *args, **options):
        if args:
            if len(args) > 1:
                raise CommandError('Command accept at most one parameter.')
            site = Site.objects.get_or_create(domain=args[0], name=args[0])
        else:
            hostname = get_host_name()
            site = Site.objects.get_or_create(domain=hostname, name=hostname)

        try:
            page = FlatPage.objects.get(url='/getting-started/')
            page.sites = site
            page.save()
        except FlatPage.DoesNotExist:
            page = FlatPage(url='/getting-started/', title='Getting Started', registration_required=False)
            page.content = 'Go to admin panel to change welcome message!'
            page.save()
            page.sites = site
            page.save()
