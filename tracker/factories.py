from datetime import datetime

import factory

from tracker.models import Category, Transaction, User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Sequence(lambda n: f"user{n}")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.Iterator(["Food", "Housing", "Salary", "Bills", "Social"])


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    amount = factory.Faker("random_int", min=1, max=1000)
    date = factory.Faker(
        "date_between",
        start_date=datetime(2024, 1, 1).date(),
        end_date=datetime.now().date(),
    )
    type = factory.Iterator([x[0] for x in Transaction.TypeChoices.choices])
