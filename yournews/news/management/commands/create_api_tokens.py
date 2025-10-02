from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class Command(BaseCommand):
    help = "Create API tokens for all existing users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Create token for specific username",
        )

    def handle(self, *args, **options):
        username = options.get("username")

        if username:
            try:
                user = User.objects.get(username=username)
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Token created for user "{username}": {token.key}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Token already exists for user "{username}": '
                            f"{token.key}"
                        )
                    )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" does not exist')
                )
        else:
            # Create tokens for all users
            users = User.objects.all()
            created_count = 0
            existing_count = 0

            for user in users:
                token, created = Token.objects.get_or_create(user=user)
                if created:
                    created_count += 1
                    self.stdout.write(
                        f"Token created for {user.username}: {token.key}"
                    )
                else:
                    existing_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Tokens created: {created_count}, "
                    f"Already existed: {existing_count}"
                )
            )
