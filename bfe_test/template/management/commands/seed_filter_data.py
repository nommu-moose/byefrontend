from django.core.management.base import BaseCommand
from template.models import DataForFiltering
from faker import Faker
import random


class Command(BaseCommand):
    """
    Quickly fills DataForFiltering with N random rows.

    Usage:
        python manage.py seed_filter_data --count 500
    """
    help = "Generate dummy rows for the DataForFiltering model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=200,
            help="How many rows to create (default: 200).",
        )

    def handle(self, *args, **options):
        fake = Faker()
        total = options["count"]
        batch = []

        self.stdout.write(f"Creating {total} rows …")

        domains = [fake.domain() for _ in range(15)]

        for _ in range(total):
            domain = random.choice([random.choice(domains),
                                    fake.domain_name(),
                                    fake.domain_name(),
                                    fake.domain_name()])
            batch.append(
                DataForFiltering(
                    name=fake.name(),
                    domain=domain,
                    birthday=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    # created / last_updated are auto-filled
                    is_active=fake.boolean(chance_of_getting_true=80),
                    is_admin=fake.boolean(chance_of_getting_true=10),
                    account_credits=round(random.uniform(0, 2000), 2),
                )
            )

        DataForFiltering.objects.bulk_create(batch, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"✔  Inserted {total} rows."))
