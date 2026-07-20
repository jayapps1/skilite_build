import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = "Creates or updates the default Skilite Build superadmin."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Reset the existing superadmin password using the .env value.",
        )

    def handle(self, *args, **options):
        # These are environment-variable names, not their values.
        username = os.getenv(
            "DJANGO_SUPERUSER_USERNAME",
            "",
        ).strip()

        email = os.getenv(
            "DJANGO_SUPERUSER_EMAIL",
            "",
        ).strip().lower()

        password = os.getenv(
            "DJANGO_SUPERUSER_PASSWORD",
            "",
        )

        missing_variables = []

        if not username:
            missing_variables.append(
                "DJANGO_SUPERUSER_USERNAME"
            )

        if not email:
            missing_variables.append(
                "DJANGO_SUPERUSER_EMAIL"
            )

        if not password:
            missing_variables.append(
                "DJANGO_SUPERUSER_PASSWORD"
            )

        if missing_variables:
            raise CommandError(
                "Missing environment variables: "
                + ", ".join(missing_variables)
            )

        User = get_user_model()

        email_conflict = (
            User.objects
            .filter(email__iexact=email)
            .exclude(username=username)
            .exists()
        )

        if email_conflict:
            raise CommandError(
                f"The email '{email}' is already assigned "
                "to another user."
            )

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
            },
        )

        user.email = email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        password_changed = False

        if created:
            user.set_password(password)
            password_changed = True

        elif options["reset_password"]:
            user.set_password(password)
            password_changed = True

        elif not user.has_usable_password():
            user.set_password(password)
            password_changed = True

        user.save()

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": (
                    "Skilite Build Administrator"
                ),
            },
        )

        if created:
            message = (
                f"Superadmin '{username}' "
                "created successfully."
            )
        else:
            message = (
                f"Superadmin '{username}' already existed "
                "and its permissions were updated."
            )

        self.stdout.write(
            self.style.SUCCESS(message)
        )

        if password_changed:
            self.stdout.write(
                self.style.SUCCESS(
                    "The superadmin password was set "
                    "from the .env file."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "The existing password was not changed. "
                    "Run with --reset-password to replace it."
                )
            )