"""
Create a test user and print auth token + credentials for testing APIs (e.g. /api/admin/orders/).
Usage: python manage.py create_test_token
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

# Default credentials (safe for local/dev only)
DEFAULT_USERNAME = "admintest"
DEFAULT_PASSWORD = "TestAdmin123!"
DEFAULT_EMAIL = "admintest@example.com"


class Command(BaseCommand):
    help = "Create a test user and print token + credentials for API testing (e.g. GET /api/admin/orders/)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=DEFAULT_USERNAME,
            help=f"Username (default: {DEFAULT_USERNAME}; use mobile number for customer-style login)",
        )
        parser.add_argument(
            "--password",
            default=DEFAULT_PASSWORD,
            help=f"Password (default: {DEFAULT_PASSWORD})",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        username = options["username"]
        password = options["password"]
        email = username + "@example.com" if "@" not in username else username

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_active": True, "is_staff": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {username} (staff)"))
        else:
            user.is_staff = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(f"User already exists, password updated: {username}"))

        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("--- Use these to test /api/admin/orders/ ---"))
        self.stdout.write("")
        self.stdout.write("Admin login (POST /api/admin/login/)")
        self.stdout.write("  username: " + username)
        self.stdout.write("  password: " + password)
        self.stdout.write("")
        self.stdout.write("Token (use in header: Authorization: Token <token>)")
        self.stdout.write("  " + token.key)
        self.stdout.write("")
        self.stdout.write("Example: List all orders")
        self.stdout.write("  curl -H \"Authorization: Token " + token.key + "\" http://localhost:8000/api/admin/orders/")
        self.stdout.write("")
        self.stdout.write("Example: Admin login to get a fresh token")
        self.stdout.write('  curl -X POST http://localhost:8000/api/admin/login/ -H "Content-Type: application/json" -d "{\\"username\\":\\"' + username + '\\",\\"password\\":\\"' + password + '\\"}"')
        self.stdout.write("")
