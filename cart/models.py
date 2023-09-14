from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from products.models import Product

User = get_user_model()

# Create your models here.


class Purchase(models.Model):

    user = models.ForeignKey(User, verbose_name=_(
        "User"), on_delete=models.CASCADE)
    content = models.JSONField(_("Content"))
    cost = models.IntegerField(_("Cost"))
    charge_id = models.CharField(_("Charge_id"), max_length=50, null=True)
    payment_status = models.CharField(
        _("Payment Status"), default="0", max_length=1)
    datetime = models.DateTimeField(
        _("Datetime"), auto_now=False, auto_now_add=True)

    class Meta:
        verbose_name = _("Purchase")
        verbose_name_plural = _("Purchases")

    def checkout(self):
        sub_totals = map(lambda content: Product.objects.get(
            id=content[0]).price*int(content[1]), self.content.items())
        total = sum(sub_totals)
        return total
