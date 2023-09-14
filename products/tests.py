from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import exceptions
from products.views import ProductViewset
from products.models import Product, Category

# Create your tests here.


class ProductViewsetTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.viewset = ProductViewset()
        cls.factory = APIRequestFactory()
        category = Category.objects.create(name="test")
        cls.category = category
        category2 = Category.objects.create(name="test2")
        Product.objects.create(name="test1", category=category,
                               description="test", price=20, amount=20, image="/static/1.png")
        Product.objects.create(name="test2", category=category2,
                               description="test", price=20, amount=20, image="/static/2.png")

    def test_get_queryset_in_list_with_category(self):
        request = self.factory.get(
            "/product/", data={"category": self.category.pk})
        self.viewset.action = 'list'
        self.viewset.request = request
        queryset = self.viewset.get_queryset()
        expected_queryset = Product.objects.all().first()
        
        self.assertEqual(list(queryset),[expected_queryset])
    
    def test_get_queryset_in_list_with_no_category(self):
        self.viewset.action = 'list'
        self.viewset.request = self.factory.get("/product/")
        with self.assertRaises(exceptions.ValidationError):
            self.viewset.get_queryset()
            
    def test_get_queryset(self):
        self.viewset.action = 'nolist'
        queryset = self.viewset.get_queryset()
        expected_queryset = Product.objects.all()
        
        self.assertEqual(list(queryset),list(expected_queryset))