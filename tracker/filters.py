import django_filters
from django import forms

from tracker.models import Category, Transaction


class TransactionFilter(django_filters.FilterSet):
    transaction_type = django_filters.ChoiceFilter(
        field_name="type",
        lookup_expr="iexact",
        choices=Transaction.TypeChoices.choices,
        empty_label="Any",
    )

    start_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="gte",
        label="Date From",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    end_date = django_filters.DateFilter(
        field_name="date",
        lookup_expr="lte",
        label="Date To",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category",  # default
        lookup_expr="exact",  # default
        label="Category",  # default
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Transaction
        fields = ("transaction_type", "start_date", "end_date", "category")
