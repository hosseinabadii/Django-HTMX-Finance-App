from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from tracker.models import Category, Transaction, User

income_type = Transaction.TypeChoices.INCOME
expense_type = Transaction.TypeChoices.EXPENSE


@pytest.mark.django_db
def test_total_values_appear_on_list_page(
    user_transactions: list[Transaction], client: Client
):
    total_income = sum(t.amount for t in user_transactions if t.type == income_type)
    total_expenses = sum(t.amount for t in user_transactions if t.type == expense_type)
    net_income = total_income - total_expenses
    user = user_transactions[0].user
    client.force_login(user)
    response = client.get(reverse("transactions-list"))

    assert response.context["total_income"] == total_income
    assert response.context["total_expenses"] == total_expenses
    assert response.context["net_income"] == net_income


@pytest.mark.django_db
def test_transaction_type_filter(user_transactions: list[Transaction], client: Client):
    user = user_transactions[0].user
    client.force_login(user)

    # income check
    GET_params = {"transaction_type": income_type}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert transaction.type == income_type

    # expense check
    GET_params = {"transaction_type": expense_type}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert transaction.type == expense_type


@pytest.mark.django_db
def test_start_end_date_filter(user_transactions: list[Transaction], client: Client):
    user = user_transactions[0].user
    client.force_login(user)
    date_cutoff = datetime.now().date() - timedelta(days=120)

    # start date check
    GET_params = {"start_date": date_cutoff}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert transaction.date >= date_cutoff

    # end date check
    GET_params = {"end_date": date_cutoff}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert transaction.date <= date_cutoff

    # start  and end date check
    start_date = datetime.now().date() - timedelta(days=150)
    end_date = datetime.now().date() - timedelta(days=100)
    GET_params = {"start_date": start_date, "end_date": end_date}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert start_date <= transaction.date <= end_date


@pytest.mark.django_db
def test_category_filter(user_transactions: list[Transaction], client: Client):
    user = user_transactions[0].user
    client.force_login(user)

    category_pks = Category.objects.all()[:2].values_list("pk", flat=True)
    GET_params = {"category": category_pks}
    response = client.get(reverse("transactions-list"), data=GET_params)
    qs: list[Transaction] = response.context["transactions_page"]

    for transaction in qs:
        assert transaction.category.pk in category_pks


@pytest.mark.django_db
def test_add_transaction_request(
    user: User, transaction_dict_params: dict, client: Client
):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()
    # headers = {"Hx-Request": "true"}
    response = client.post(
        path=reverse("create-transaction"),
        data=transaction_dict_params,
        # headers=headers,
    )

    assert Transaction.objects.filter(user=user).count() == user_transaction_count + 1
    assertTemplateUsed(response, "tracker/partials/transaction-success.html")


@pytest.mark.django_db
def test_cannot_add_transaction_with_negative_amount(
    user: User, transaction_dict_params: dict, client: Client
):
    client.force_login(user)
    user_transaction_count = Transaction.objects.filter(user=user).count()
    transaction_dict_params["amount"] = -44
    response = client.post(
        path=reverse("create-transaction"),
        data=transaction_dict_params,
    )

    assert Transaction.objects.filter(user=user).count() == user_transaction_count
    assertTemplateUsed(response, "tracker/partials/create-transaction.html")
    assert "Hx-Retarget" in response.headers


@pytest.mark.django_db
def test_update_transaction_request(
    user: User, transaction_dict_params: dict, client: Client
):
    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()
    now = datetime.now().date()
    transaction_dict_params["amount"] = 999
    transaction_dict_params["date"] = now
    client.post(
        path=reverse("update-transaction", kwargs={"pk": transaction.pk}),
        data=transaction_dict_params,
    )

    assert Transaction.objects.filter(user=user).count() == 1
    transaction = Transaction.objects.first()
    assert transaction.amount == 999
    assert transaction.date == now


@pytest.mark.django_db
def test_delete_transaction_request(
    user: User, transaction_dict_params: dict, client: Client
):
    client.force_login(user)
    assert Transaction.objects.filter(user=user).count() == 1

    transaction = Transaction.objects.first()
    client.delete(reverse("delete-transaction", kwargs={"pk": transaction.pk}))
    assert Transaction.objects.filter(user=user).count() == 0
