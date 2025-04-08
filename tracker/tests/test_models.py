import pytest

from tracker.models import Transaction

income_type = Transaction.TypeChoices.INCOME
expense_type = Transaction.TypeChoices.EXPENSE


@pytest.mark.django_db
def test_queryset_get_income_method(transactions: list[Transaction]):
    qs: list[Transaction] = Transaction.objects.get_income()
    assert qs.count() > 0
    assert all(t.type == income_type for t in qs)


@pytest.mark.django_db
def test_queryset_get_expenses_method(transactions: list[Transaction]):
    qs: list[Transaction] = Transaction.objects.get_expenses()
    assert qs.count() > 0
    assert all(t.type == expense_type for t in qs)


@pytest.mark.django_db
def test_queryset_get_total_income_method(transactions: list[Transaction]):
    total = sum(t.amount for t in transactions if t.type == income_type)
    assert Transaction.objects.get_total_income() == total


@pytest.mark.django_db
def test_queryset_get_total_expenses_method(transactions: list[Transaction]):
    total = sum(t.amount for t in transactions if t.type == expense_type)
    assert Transaction.objects.get_total_expenses() == total
