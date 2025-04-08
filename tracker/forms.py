from django import forms
from django.utils import timezone

from tracker.models import Category, Transaction


class TransactionForm(forms.ModelForm):
    type = forms.ChoiceField(
        choices=Transaction.TypeChoices.choices,
    )
    date = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.RadioSelect(),
    )

    class Meta:
        model = Transaction
        fields = ("type", "amount", "date", "category")

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number")
        return amount
