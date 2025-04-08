from django.urls import path

from tracker import views

urlpatterns = [
    path("", views.index, name="index"),
    path("transactions/", views.transactions_list, name="transactions-list"),
    path("transactions/create/", views.create_transaction, name="create-transaction"),
    path(
        "transactions/<int:pk>/update/",
        views.update_transaction,
        name="update-transaction",
    ),
    path(
        "transactions/<int:pk>/delete/",
        views.delete_transaction,
        name="delete-transaction",
    ),
    path("transactions/charts/", views.transactions_charts, name="transactions-charts"),
    path("transactions/export/", views.transactions_export, name="transactions-export"),
    path("transactions/import/", views.transactions_import, name="transactions-import"),
]
