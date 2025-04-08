from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django_htmx.http import retarget
from tablib import Dataset

from tracker.charting import plot_category_pie_chart, plot_income_expenses_bar_chart
from tracker.filters import TransactionFilter
from tracker.forms import TransactionForm
from tracker.managers import TransactionQuerySet
from tracker.models import Transaction
from tracker.resources import TransactionResource


def index(request: HttpRequest):
    return render(request, "tracker/index.html")


@login_required
def transactions_list(request: HttpRequest):
    transaction_filter = TransactionFilter(
        data=request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )
    paginator = Paginator(
        object_list=transaction_filter.qs,
        per_page=settings.PAGE_SIZE,
    )

    page = request.GET.get("page")
    if page and request.htmx:
        # import time

        # time.sleep(0.5)
        context = {"transactions_page": paginator.page(page)}
        return render(
            request,
            "tracker/partials/transactions-container.html#transaction_list",
            context,
        )
    total_income = transaction_filter.qs.get_total_income()
    total_expenses = transaction_filter.qs.get_total_expenses()

    context = {
        "transactions_page": paginator.page(1),
        "filter_form": transaction_filter.form,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_income": total_income - total_expenses,
    }

    if request.htmx:
        return render(request, "tracker/partials/transactions-container.html", context)
    return render(request, "tracker/transactions-list.html", context)


@login_required
def create_transaction(request: HttpRequest):
    if request.method == "POST":
        form = TransactionForm(data=request.POST)
        if form.is_valid():
            transaction: Transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            context = {"message": "Transaction was added successfully!"}
            return render(request, "tracker/partials/transaction-success.html", context)
        else:
            context = {"form": form}
            response = render(
                request, "tracker/partials/create-transaction.html", context
            )
            return retarget(response, "#transaction-block")
    context = {"form": TransactionForm()}
    return render(request, "tracker/partials/create-transaction.html", context)


@login_required
def update_transaction(request: HttpRequest, pk: int):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == "POST":
        form = TransactionForm(data=request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            context = {"message": "Transaction was updated successfully!"}
            return render(request, "tracker/partials/transaction-success.html", context)
        context = {"form": form, "pk": pk}
        response = render(request, "tracker/partials/update-transaction.html", context)
        return retarget(response, "#transaction-block")

    context = {"form": TransactionForm(instance=transaction), "pk": pk}
    return render(request, "tracker/partials/update-transaction.html", context)


@login_required
@require_http_methods(["DELETE"])
def delete_transaction(request: HttpRequest, pk: int):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    context = {
        "message": f"Transaction of ${transaction.amount} on {transaction.date} was deleted successfully!"
    }
    return render(request, "tracker/partials/transaction-success.html", context)


@login_required
def transactions_charts(request: HttpRequest):
    transaction_filter = TransactionFilter(
        data=request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )
    qs: TransactionQuerySet = transaction_filter.qs
    income_expense_barchart = plot_income_expenses_bar_chart(qs)
    category_income_pie = plot_category_pie_chart(qs.get_income())
    category_expense_pie = plot_category_pie_chart(qs.get_expenses())
    context = {
        "filter_form": transaction_filter.form,
        "income_expense_barchart": income_expense_barchart.to_html(),
        "category_income_pie": category_income_pie.to_html(),
        "category_expense_pie": category_expense_pie.to_html(),
    }
    if request.htmx:
        return render(request, "tracker/partials/charts-container.html", context)
    return render(request, "tracker/charts.html", context)


@login_required
def transactions_export(request: HttpRequest):
    if request.htmx:
        return HttpResponse(headers={"HX-Redirect": request.get_full_path()})

    transaction_filter = TransactionFilter(
        data=request.GET,
        queryset=Transaction.objects.filter(user=request.user).select_related(
            "category"
        ),
    )
    data = TransactionResource().export(transaction_filter.qs)
    return HttpResponse(
        content=data.csv,
        headers={"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@login_required
def transactions_import(request: HttpRequest):
    if request.method == "POST":
        file = request.FILES.get("file")
        resource = TransactionResource()
        dataset = Dataset()
        dataset.load(file.read().decode(), format="csv")
        result = resource.import_data(dataset, user=request.user, dry_run=True)

        for row in result:
            for error in row.errors:
                print(error)

        if not result.has_errors():
            resource.import_data(dataset, user=request.user, dry_run=False)
            context = {
                "message": f"{result.total_rows} transactions were uploaded successfully "
                f"({result.totals['new']} new, {result.totals['update']} skipped)"
            }
        else:
            context = {"message": "Sorry, an error occurred."}
        return render(request, "tracker/partials/transaction-success.html", context)
    return render(request, "tracker/partials/import-transaction.html")
