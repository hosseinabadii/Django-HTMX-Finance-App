from django.contrib import admin

from tracker.models import Category, Transaction, User

admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Category)
