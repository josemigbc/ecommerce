import datetime

from django.utils import timezone
from rest_framework import permissions, status, exceptions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView

from .models import Purchase
from .serializers import PurchaseSerializer

# Create your views here.


class PurchaseViewset(GenericViewSet, ListCreateAPIView, RetrieveAPIView):
    serializer_class = PurchaseSerializer
    queryset = Purchase.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        to_delete = self.queryset.filter(payment_status="0",
                                         datetime__lt=timezone.now()-datetime.timedelta(minutes=10)
                                         )
        to_delete.delete()
        return self.queryset.filter(user=self.request.user)

    def get_serializer(self, *args, **kwargs):
        data = kwargs.get("data")
        if data:
            try:
                data["user"] = self.request.user.pk
            except:
                raise exceptions.ValidationError(
                    detail={"The content must be application/json."})

        return super().get_serializer(*args, **kwargs)
