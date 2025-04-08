import random

from django.core.management.base import BaseCommand
from faker import Faker

from tracker.models import Category, Transaction, User

CATEGORIES = [
    "Bills",
    "Food",
    "Clothes",
    "Medical",
    "Housing",
    "Salary",
    "Social",
    "Transport",
    "Vacation",
]


class Command(BaseCommand):
    help = "Generates transactions for testing"

    def handle(self, *args, **options):
        print("Removing old data...")
        User.objects.all().delete()
        Category.objects.all().delete()
        Transaction.objects.all().delete()

        print("Populating database...")
        fake = Faker()

        for category in CATEGORIES:
            Category.objects.create(name=category)

        user = User.objects.filter(username="admin").first()
        if not user:
            user = User.objects.create_user(username="user", password="test")

        categories = Category.objects.all()
        types = [type[0] for type in Transaction.TypeChoices.choices]
        for _ in range(100):
            Transaction.objects.create(
                user=user,
                category=random.choice(categories),
                type=random.choice(types),
                amount=random.uniform(1, 2500),
                date=fake.date_between(start_date="-1y", end_date="today"),
            )
        print("Successfully Done!")
