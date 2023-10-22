from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
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
                raise ValidationError(detail={"error":"Missing param category"})
            return self.queryset.filter(category=category)
        if self.action == 'discount':
            return self.queryset.filter(discount__gt=0)
        return super().get_queryset()
    
    @action(detail=False,methods=['get'])
    def discount(self,request):
        return self.list(request)
    
class ProductImageView(View):
    def get(self,request,filename):
        return FileResponse(open(f"media/{filename}","rb"))
