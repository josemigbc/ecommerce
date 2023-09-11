from django.db.models.signals import pre_save,post_save,post_delete
from django.dispatch import receiver
from products.models import Product
from .models import Purchase

@receiver(pre_save,sender=Purchase)
def set_cost(sender,instance, **kwargs):
    instance.cost = instance.checkout()
    
@receiver(post_save,sender=Purchase)
def reduce_product_amount(sender,instance,created,*args, **kwargs):
    if created:
        for prod,amount in instance.content.items():
            prod = Product.objects.get(id=prod)
            prod.amount -= int(amount)
            prod.save()

@receiver(post_delete,sender=Purchase)
def increase_product_amount(sender,instance,*args, **kwargs):
    for prod,amount in instance.content.items():
        prod = Product.objects.get(id=prod)
        prod.amount += int(amount)
        prod.save()