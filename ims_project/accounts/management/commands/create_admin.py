from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from getpass import getpass
from accounts.models import User


class Command(BaseCommand):
    help = (
        'Creates the first System Admin account for the Internship Management '
        'System. This is the ONLY account this command creates — no sample '
        'students, organisations, or internship records are added. Everything '
        'else should be entered through the website by your team.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username (will prompt if not given)')
        parser.add_argument('--email', type=str, default='', help='Admin email (optional)')
        parser.add_argument('--first-name', type=str, default='', help='Admin first name (optional)')
        parser.add_argument('--last-name', type=str, default='', help='Admin last name (optional)')

    @transaction.atomic
    def handle(self, *args, **options):
        username = options.get('username')
        if not username:
            username = input('System Admin username: ').strip()
        if not username:
            raise CommandError('Username is required.')

        if User.objects.filter(username=username).exists():
            raise CommandError(f'A user named "{username}" already exists.')

        email = options.get('email') or input('Email (optional, press Enter to skip): ').strip()
        first_name = options.get('first_name') or input('First name (optional): ').strip()
        last_name = options.get('last_name') or input('Last name (optional): ').strip()

        password = getpass('Password: ')
        password_confirm = getpass('Password (again): ')
        if password != password_confirm:
            raise CommandError('Passwords did not match.')
        if len(password) < 8:
            raise CommandError('Password must be at least 8 characters.')

        admin = User.objects.create_superuser(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        # save() on the User model auto-promotes superusers to role='system_admin'
        admin.save()

        self.stdout.write(self.style.SUCCESS(f'\nSystem Admin account "{username}" created.'))
        self.stdout.write('Log in at /accounts/login/ and start entering real data:')
        self.stdout.write('  1. Students > Programmes  — add your programme(s)')
        self.stdout.write('  2. Students > Batches     — add your batch(es)')
        self.stdout.write('  3. Organisations          — add organisations/advocates as they come in')
        self.stdout.write('  4. Students               — add student profiles')
        self.stdout.write('  5. Internship Records, Mentor Assignments, Marks — as the term progresses')
        self.stdout.write('  6. User Management        — create accounts for faculty, evaluators, HoD, students')
