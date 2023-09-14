from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from products.models import Product, Category
from cart.models import Purchase
from cart.serializers import PurchaseSerializer
from cart.views import PurchaseViewset
import freezegun

User = get_user_model()


class PurchaseModelTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        category = Category.objects.create(name="test")
        cls.product1 = Product.objects.create(name="test1", category=category,
                                              description="test", price=20, amount=20, image="/static/1.png")
        cls.product2 = Product.objects.create(name="test2", category=category,
                                              description="test", price=20, amount=20, image="/static/2.png")
        cls.user = User.objects.create_user(
            username="test", password="testing1234")

    def test_checkout_and_signal(self):
        purchase = Purchase.objects.create(
            user=self.user, content={self.product1.pk: 2, self.product2.pk: 4})
        self.assertEqual(purchase.cost, 120)
        self.assertEqual(purchase.checkout(), 120)
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product1.amount, 18)
        self.assertEqual(self.product2.amount, 16)

        purchase.delete()
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product1.amount, 20)
        self.assertEqual(self.product2.amount, 20)


class PurchaseSerializerTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        category = Category.objects.create(name="test")
        cls.product1 = Product.objects.create(name="test1", category=category,
                                              description="test", price=20, amount=20, image="/static/1.png")
        cls.product2 = Product.objects.create(name="test2", category=category,
                                              description="test", price=20, amount=20, image="/static/2.png")
        cls.user = User.objects.create_user(
            username="test", password="testing1234")

    def test_is_valid_with_ok(self):
        serializer = PurchaseSerializer(data={"user": self.user.pk, "content": {
                                        self.product1.pk: 2, self.product2.pk: 4}})
        valid = serializer.is_valid()
        self.assertTrue(valid)

    def test_is_valid_with_product_does_not_exist(self):
        serializer = PurchaseSerializer(data={"user": self.user, "content": {
                                        100: 2, self.product2.pk: 4}})
        valid = serializer.is_valid()
        self.assertFalse(valid)

        with self.assertRaises(exceptions.ValidationError):
            valid = serializer.is_valid(raise_exception=True)

    def test_is_valid_with_product_gt_amount(self):
        serializer = PurchaseSerializer(data={"user": self.user, "content": {
                                        self.product1.pk: 23, self.product2.pk: 4}})
        valid = serializer.is_valid()
        self.assertFalse(valid)

    def test_is_valid_with_product_equal_amount(self):
        serializer = PurchaseSerializer(data={"user": self.user.pk, "content": {
                                        self.product1.pk: 20, self.product2.pk: 4}})
        valid = serializer.is_valid()
        self.assertTrue(valid)


class PurchaseViewsetTest(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.viewset = PurchaseViewset()
        cls.factory = APIRequestFactory()
        category = Category.objects.create(name="test")
        cls.product1 = Product.objects.create(name="test1", category=category,
                                              description="test", price=20, amount=20, image="/static/1.png")
        cls.product2 = Product.objects.create(name="test2", category=category,
                                              description="test", price=20, amount=20, image="/static/2.png")
        cls.user = User.objects.create_user(
            username="test", password="testing1234")

    def test_get_queryset(self):
        with freezegun.freeze_time("2023-09-13 12:00"):
            purchase1 = Purchase.objects.create(
                user=self.user, content={self.product1.pk: 20, self.product2.pk: 4})

        with freezegun.freeze_time("2023-09-13 12:05"):
            purchase2 = Purchase.objects.create(
                user=self.user, content={self.product1.pk: 20, self.product2.pk: 4})

        with freezegun.freeze_time("2023-09-13 12:11"):
            request = APIRequestFactory("/purchase/")
            request.user = self.user
            self.viewset.request = request
            queryset = self.viewset.get_queryset()
            expected_queryset = [purchase2]
            self.assertEqual(list(queryset), expected_queryset)

    def test_get_serializer_with_data(self):
        data = {"content": {self.product1.pk: 20, self.product2.pk: 4}}
        request = APIRequestFactory("/purchase/",data=data)
        request.user = self.user
        self.viewset.format_kwarg = {}
        self.viewset.request = request
        serializer = self.viewset.get_serializer(data=data)
        data.update({"user":self.user.pk})
        expected_serializer = PurchaseSerializer(data=data)
        
        self.assertEqual(expected_serializer.initial_data,serializer.initial_data)
        
    def test_get_serializer_without_data(self):
        request = self.factory.get("/purchase/")
        request.user = self.user
        self.viewset.format_kwarg = {}
        self.viewset.request = request
        purchase = Purchase.objects.create(user=self.user,content={self.product1.pk: 20, self.product2.pk: 4})
        serializer = self.viewset.get_serializer(purchase)
        expected_serializer = PurchaseSerializer(purchase)
        
        self.assertEqual(expected_serializer.instance,serializer.instance)
        
    def test_update(self):
        purchase = Purchase.objects.create(
                user=self.user, content={self.product1.pk: 20, self.product2.pk: 4})
        request = self.factory.patch(f"/purchase/{purchase.pk}/")
        request.user = self.user
        response = self.viewset.update(request)
        
        self.assertEqual(response.status_code,405)