from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import ValidationError
from django.views import View
from django.http import FileResponse
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

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
                raise ValidationError(detail="Missing param category", code=400)
            return self.queryset.filter(category=category)
        return super().get_queryset()
    
class ProductImageView(View):
    def get(self,request,filename):
        return FileResponse(open(f"media/{filename}","rb"))
