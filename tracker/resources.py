from import_export import resources
from import_export.fields import Field
from import_export.widgets import DateWidget, ForeignKeyWidget, NumberWidget

from tracker.models import Category, Transaction


class TransactionResource(resources.ModelResource):
    amount = Field(attribute="amount", widget=NumberWidget())
    date = Field(attribute="date", widget=DateWidget(format="%m/%d/%Y"))
    category = Field(
        column_name="category",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="name"),
    )

    def after_init_instance(self, instance, new, row, **kwargs):
        instance.user = kwargs.get("user")

    class Meta:
        model = Transaction
        fields = ("amount", "type", "date", "category")
        import_id_fields = ("amount", "type", "date", "category")
