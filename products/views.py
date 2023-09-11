from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from .models import Category,Product
from .serializers import CategorySerializer,ProductSerializer

# Create your views here.
class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

class ProductViewset(ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    def get_queryset(self):
        if self.action == "list":
            category = self.request.GET.get('category')
            if not category:
                raise APIException(detail="Missing param category",code=400)
            return self.queryset.filter(category=category)
        return super().get_queryset()
    
    def handle_exception(self, exc):
        if isinstance(exc,APIException):
            return Response(data=str(exc),status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)