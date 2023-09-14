from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Category(models.Model):

    name = models.CharField(_("Name"), max_length=50)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name


class Product(models.Model):

    name = models.CharField(_("Name"), max_length=50)
    description = models.TextField(_("Description"))
    category = models.ForeignKey(Category, verbose_name=_(
        "Category"), on_delete=models.CASCADE)
    price = models.IntegerField(_("Price"))
    image = models.CharField(_("Image URL"), max_length=200)
    amount = models.IntegerField(_("Amount"))

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.name
