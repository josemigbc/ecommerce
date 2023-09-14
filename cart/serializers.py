from rest_framework.serializers import ModelSerializer
from rest_framework import exceptions

from products.models import Product

from .models import Purchase


class PurchaseSerializer(ModelSerializer):

    class Meta:
        model = Purchase
        fields = "__all__"
        read_only_fields = ("payment_status", "cost","charge_id")

    def is_valid(self, *, raise_exception=False):
        error = {}
        try:
            for product_id, amount in self.initial_data["content"].items():
                if Product.objects.get(id=product_id).amount < amount:
                    error = {'error':{"content": ["The amount of product is not avaible"]}}
                    break
        except:
            error = {'error':{"content":["One of products does not exit."]}}
        if error:
            if raise_exception:
                raise exceptions.ValidationError(error)
            return False
        return super().is_valid(raise_exception=raise_exception)
