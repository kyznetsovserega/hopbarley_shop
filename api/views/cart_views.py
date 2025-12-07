"""
API ViewSet корзины.

Использует CartService — слой бизнес-логики,
синхронизированный с WEB-версией:

- добавление объединяет количество
- проверка stock
- нет дублей CartItem
- увеличение / уменьшение / удаление
"""

from __future__ import annotations

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError

from cart.models import CartItem
from cart.services import CartService
from api.serializers.cart_serializers import CartItemSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    """
    API корзины.

    Доступ:
    - Только авторизованные пользователи (JWT)
    - Корзина привязана к request.user
    """

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"

    # ---------------------------------------------------------------------
    # Основной queryset
    # ---------------------------------------------------------------------
    def get_queryset(self):
        """
        Возвращает корзину текущего пользователя.
        """
        return (
            CartItem.objects
            .filter(user=self.request.user)
            .select_related("product")
        )

    # ---------------------------------------------------------------------
    # Создание элемента корзины
    # ---------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        """
        POST /api/cart/

        Поведение:
        - если товар уже есть > увеличиваем количество
        - если нет > создаём новую запись
        """

        product_id = request.data.get("product")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response(
                {"error": "Field 'product' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = CartService(request)

        try:
            product = service._resolve_product(product_id)
            item = service.add(product, quantity)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---------------------------------------------------------------------
    # Обновление quantity
    # ---------------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        """
        PATCH /api/cart/<id>/

        Позволяет изменить количество напрямую.
        """

        service = CartService(request)
        item = service._get_cart_item(kwargs["pk"])

        try:
            new_qty = int(request.data.get("quantity", 1))
        except (TypeError, ValueError):
            return Response({"error": "Quantity must be a number"}, status=400)

        if new_qty < 1:
            return Response({"error": "Quantity must be >= 1"}, status=400)

        diff = new_qty - item.quantity

        try:
            if diff > 0:
                service.add(item.product, diff)
            elif diff < 0:
                for _ in range(abs(diff)):
                    service.decrease(item.id)
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)

        item = service._get_cart_item(item.id)
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    # ---------------------------------------------------------------------
    # Удаление элемента корзины
    # ---------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        service = CartService(request)
        service.remove(kwargs["pk"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ---------------------------------------------------------------------
    # Очистить корзину
    # ---------------------------------------------------------------------
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        service = CartService(request)
        service.clear()
        return Response({"status": "cart cleared"})
