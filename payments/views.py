from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
from cart.models import Purchase
from django.conf import settings
from django.utils import timezone
import stripe

def proccess_payment(charge_token,price):
    """
    Args:
        charge_token (str): Token generated in fronted using information of card.
        price (int): price of product

    Returns:
        Charge: Object Charge returned by creation of charge. 
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    charge = stripe.Charge.create(
        amount=price,
        currency="usd",
        description="Purchase of a ticket",
        source=charge_token
    )
    
    return charge

class PaymentView(APIView):
    
    def post(self,request):
        try:
            charge_token = request.data['charge_token']
            purchase_id = request.data['purchase']
            purchase = Purchase.objects.get(id=purchase_id)
            spent = timezone.now() - purchase.datetime
            
            if spent.seconds > 600:
                purchase.delete()
                raise exceptions.ValidationError(detail={'error': 'This purchase is timeout because spent over 10 minutes.'})
            
            charge = proccess_payment(charge_token,purchase.cost)
        
        except KeyError:
            return Response(
                data={"message": "The charge token and reservation id must be given."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except stripe.error.CardError as e:
            return Response(data={"message":str(e)},status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            return Response(data={"message": str(e)},status=status.HTTP_404_NOT_FOUND)
        
        purchase.payment_status = "1"
        purchase.charge_id = charge.id
        purchase.save()
        
        return Response(data=charge.to_dict())
