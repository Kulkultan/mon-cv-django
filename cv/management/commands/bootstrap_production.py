import os
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command

from cv.models import Profile

LEGACY_PUBLIC_EMAIL = "zaddywilfriedlegre@gmail.com"
DEFAULT_PUBLIC_EMAIL = "contact@zaddywilfriedlegre.com"


class Command(BaseCommand):
    help = "Load initial CV data when the database is empty and create/update a superuser from environment variables."

    def handle(self, *args, **options):
        fixture_path = Path(settings.BASE_DIR) / "cv" / "fixtures" / "cv_data.json"
        fixture_relpath = "cv/fixtures/cv_data.json"

        if fixture_path.exists() and not Profile.objects.exists():
            call_command("loaddata", fixture_relpath, verbosity=0)
            self.stdout.write(self.style.SUCCESS("Initial CV data loaded."))
        else:
            self.stdout.write("Initial CV data already present or fixture missing.")

        public_email = os.environ.get("PUBLIC_CONTACT_EMAIL", DEFAULT_PUBLIC_EMAIL)
        updated_profiles = Profile.objects.filter(email__in=["", LEGACY_PUBLIC_EMAIL]).update(email=public_email)
        if updated_profiles:
            self.stdout.write(self.style.SUCCESS(f"Updated public contact email on {updated_profiles} profile(s)."))

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD is missing; skipped superuser bootstrap."
                )
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        user.is_staff = True
        user.is_superuser = True
        if email:
            user.email = email
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' updated."))
