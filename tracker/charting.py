import plotly.express as px
from django.db.models import Sum

from tracker.managers import TransactionQuerySet
from tracker.models import Category


def plot_income_expenses_bar_chart(qs: TransactionQuerySet):
    x_val = ["Income", "Expenditure"]
    total_income = qs.get_total_income()
    total_expenses = qs.get_total_expenses()

    fig = px.bar(x=x_val, y=[total_income, total_expenses])
    return fig


def plot_category_pie_chart(qs: TransactionQuerySet):
    count_per_category = (
        qs.order_by("category")
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("category")
    )
    category_pks = count_per_category.values_list("category", flat=True)
    total_amounts = count_per_category.values_list("total", flat=True)
    categories = (
        Category.objects.filter(pk__in=category_pks)
        .order_by("pk")
        .values_list("name", flat=True)
    )
    fig = px.pie(names=categories, values=total_amounts)
    fig.update_layout(title="Total Amount per Category")
    return fig
