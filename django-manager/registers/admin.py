from django.conf import settings
from django.contrib import admin

from .models import Product, Receipt, Sell


class SellInline(admin.TabularInline):
    model = Sell
    extra = 1


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    inlines = [
        SellInline,
    ]

    def save_related(self, request, form, formsets, change):
        """
        Publish data to registered `Adapters`.
        """
        # save the model as usual
        super().save_related(request, form, formsets, change)
        instance = form.instance
        # push data
        for adapter in settings.PUSH_ADAPTERS:
            adapter.push(instance)


admin.site.register(Product)
