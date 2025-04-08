import pytest

from tracker.factories import TransactionFactory, UserFactory
from tracker.models import Transaction, User


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def transactions() -> list[Transaction]:
    return TransactionFactory.create_batch(20)


@pytest.fixture
def user_transactions(user) -> list[Transaction]:
    return TransactionFactory.create_batch(20, user=user)


@pytest.fixture
def transaction_dict_params(user) -> dict:
    transaction: Transaction = TransactionFactory.create(user=user)
    return {
        "type": transaction.type,
        "category": transaction.category.pk,
        "date": transaction.date,
        "amount": transaction.amount,
    }
