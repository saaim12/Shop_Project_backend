from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.orders.serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer
from apps.orders.services import OrderService
from config.response import error_response, extract_error_message, success_response


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = OrderService.list_orders_for_user(request.user)
        return success_response([OrderSerializer(order).data for order in orders], message="Orders fetched successfully")

    def post(self, request):
        role = (getattr(request.user, "role", "") or "").upper()
        if role != "CUSTOMER":
            return error_response("Only customers can place orders", status.HTTP_403_FORBIDDEN)

        serializer = OrderCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        try:
            order = OrderService.create_order(serializer.validated_data, request.user)
        except ValueError as exc:
            return error_response(str(exc), status.HTTP_400_BAD_REQUEST)

        return success_response(OrderSerializer(order).data, status.HTTP_201_CREATED, "Order created successfully")


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        role = (getattr(request.user, "role", "") or "").upper()
        if role == "CUSTOMER" and str(order.customer.id) != str(request.user.id):
            return error_response("Forbidden", status.HTTP_403_FORBIDDEN)

        return success_response(OrderSerializer(order).data, message="Order fetched successfully")

    def patch(self, request, order_id):
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        role = (getattr(request.user, "role", "") or "").upper()
        if role not in {"STAFF", "ADMIN"}:
            return error_response("Only staff or admin can update order status", status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(extract_error_message(serializer.errors), status.HTTP_400_BAD_REQUEST)

        order = OrderService.update_order_status(order, serializer.validated_data["status"])
        return success_response(OrderSerializer(order).data, message="Order updated successfully")

    def delete(self, request, order_id):
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return error_response("Order not found", status.HTTP_404_NOT_FOUND)

        role = (getattr(request.user, "role", "") or "").upper()
        if role != "CUSTOMER":
            return error_response("Only customers can delete orders", status.HTTP_403_FORBIDDEN)

        if str(order.customer.id) != str(request.user.id):
            return error_response("Forbidden", status.HTTP_403_FORBIDDEN)

        OrderService.delete_order(order)
        return success_response({"deleted": True}, message="Order deleted successfully")
