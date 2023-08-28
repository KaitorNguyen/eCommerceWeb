from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view
from rest_framework.views import Response
from .models import Order, OrderDetail, PaymentMethod
import shops
from .serializers import (
    PaymentMethodSerializer,
    OrderDetailSerializer
)
import random

# Create your views here.
class PaymentMethodViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = PaymentMethod.objects.filter(active=True)
    serializer_class = PaymentMethodSerializer

class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView, generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        try:
            receiver_name = request.data.get('receiver_name')
            receiver_phone = request.data.get('receiver_phone')
            receiver_address = request.data.get('receiver_address')

            payment_method = PaymentMethod.objects.get(id=request.data.get('payment_method'), active=True)
            order_details = request.data.get('order_details')
        except:
            return Response({'error': 'Bạn cần phải điền đầy đủ thông tin'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            name='HD{}'.format(random.randint(100000, 900000)),
            receiver_name=receiver_name,
            receiver_phone=receiver_phone,
            receiver_address=receiver_address,
            total_price=sum(item['quantity'] * float(item['unit_price']) for item in order_details),
            payment_method=payment_method
        )
        if user.is_authenticated:
            order.user = user
        order.save()

        if order_details:
            for item in order_details:
                get_product = shops.models.Product.objects.get(id=item['product'])
                order_data = OrderDetail.objects.create(
                    order=order,
                    product=get_product,
                    quantity=item['quantity'],
                    unit_price=item['unit_price']
                )
                order_data.save()
        else:
            return Response({'error': 'Bạn không có sản phẩm nào tồn tại trong giỏ hàng!!!'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderDetailSerializer(order).data, status.HTTP_201_CREATED)


