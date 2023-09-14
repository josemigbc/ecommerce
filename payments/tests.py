from rest_framework.test import APITestCase, APIRequestFactory
from unittest.mock import MagicMock, patch
from payments.views import proccess_payment, PaymentView
from cart.models import Purchase
from products.models import Product, Category
from django.contrib.auth import get_user_model

import datetime
import stripe
import freezegun

User = get_user_model()

# Create your tests here.


class PaymentsTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        category = Category.objects.create(name="test")
        product1 = Product.objects.create(name="test1", category=category,
                                          description="test", price=20, amount=20, image="/static/1.png")
        product2 = Product.objects.create(name="test2", category=category,
                                          description="test", price=20, amount=20, image="/static/2.png")
        user = User.objects.create_user(
            username="test", password="testing1234")
        cls.purchase = Purchase.objects.create(
            user=user, content={product1.pk: 20, product2.pk: 4})

    @patch('stripe.Charge.create')
    def test_process_payment(self, mock: MagicMock):
        mock.return_value = "Charge"
        charge = proccess_payment("token", 100)
        mock.assert_called_once()
        self.assertEqual(charge, "Charge")

    @patch('stripe.Charge.create')
    def test_view_with_ok(self, mock: MagicMock):
        mock_charge = MagicMock()
        mock_charge.id = "id"
        mock_charge.to_dict.return_value = {"info": "test"}
        mock.return_value = mock_charge

        response = self.client.post(
            "/payment/", data={"charge_token": "tok", "purchase": self.purchase.pk})
        purchase = Purchase.objects.get(id=self.purchase.pk)

        self.assertEqual(response.json(), {"info": "test"})
        self.assertEqual(purchase.charge_id, "id")
        self.assertEqual(purchase.payment_status, "1")

    def test_view_with_missing_params(self):
        response = self.client.post("/payment/", data={"charge_token": "tok"})
        self.assertEqual(response.status_code, 400)

    def test_view_with_reservation_does_not_exist(self):
        response = self.client.post(
            "/payment/", data={"charge_token": "tok", "purchase": 2000})
        self.assertEqual(response.status_code, 404)

    @patch('stripe.Charge.create')
    def test_view_with_bad_token(self, mock: MagicMock):
        mock.side_effect = stripe.error.CardError(
            message="Error", code="card_decline", param="number")
        response = self.client.post(
            "/payment/", data={"charge_token": "tok", "purchase": self.purchase.pk})
        mock.assert_called_once()
        self.assertEqual(response.status_code, 401)

    def test_reservation_timeout(self):
        freeze = self.purchase.datetime + datetime.timedelta(minutes=11)
        with freezegun.freeze_time(freeze):
            response = self.client.post(
                "/payment/", data={"charge_token": "tok", "purchase": self.purchase.pk})
            self.assertEqual(response.status_code, 404)

        with self.assertRaises(Exception):
            Purchase.objects.get(id=self.purchase.pk)
