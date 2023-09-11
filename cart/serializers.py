from rest_framework.serializers import ModelSerializer
from products.models import Product
from .models import Purchase

class PurchaseSerializer(ModelSerializer):
    
    class Meta:
        model = Purchase
        fields = "__all__"
        read_only_fields = ("payment_status","cost")
        
    def is_valid(self, *, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        try:
            for product_id,amount in self.validated_data["content"].items():
                if Product.objects.get(id=product_id).amount < amount:
                    valid = False
                    self.errors["content"] = ["The amount of product is not avaible"]
                    break
        except:
            valid = False
            self.errors["content"] = ["One of products does not exit."]
            
        return valid