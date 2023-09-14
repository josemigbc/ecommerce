import datetime

from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Purchase
from .serializers import PurchaseSerializer

# Create your views here.


class PurchaseViewset(ModelViewSet):
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
            data["user"] = self.request.user.pk

        return super().get_serializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
