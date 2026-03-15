from bson import ObjectId

from apps.orders.models import Order
from apps.spare_parts.models import SparePart


class OrderService:
    @staticmethod
    def _get_spare_part(part_id):
        try:
            return SparePart.objects(id=ObjectId(part_id)).first()
        except Exception:
            return None

    @staticmethod
    def create_order(payload, customer):
        spare_part_id = payload.get("spare_part_id")
        quantity = int(payload.get("quantity", 1))

        if not spare_part_id:
            spare_part_ids = payload.get("spare_part_ids", [])
            if len(spare_part_ids) != 1:
                raise ValueError("Order must contain exactly one spare part")
            spare_part_id = spare_part_ids[0]

        spare_part = OrderService._get_spare_part(spare_part_id)
        if not spare_part:
            raise ValueError(f"Spare part not found: {spare_part_id}")

        available_quantity = float(getattr(spare_part, "quantity", 0))
        if quantity > available_quantity:
            raise ValueError("Requested quantity is greater than available stock")

        spare_part.quantity = available_quantity - quantity
        spare_part.save()

        total_price = float(spare_part.price) * quantity

        order = Order(
            customer=customer,
            spare_part=spare_part,
            quantity=quantity,
            spare_parts=[spare_part],
            total_price=total_price,
            status=Order.STATUS_PENDING,
        )
        order.save()
        return order

    @staticmethod
    def list_orders_for_user(user):
        role = (getattr(user, "role", "") or "").upper()
        if role in {"STAFF", "ADMIN"}:
            return Order.objects().order_by("-created_at")
        return Order.objects(customer=user).order_by("-created_at")

    @staticmethod
    def get_order_by_id(order_id):
        try:
            return Order.objects(id=ObjectId(order_id)).first()
        except Exception:
            return None

    @staticmethod
    def update_order_status(order, status_value):
        order.status = status_value
        order.save()
        return order

    @staticmethod
    def delete_order(order):
        spare_part = getattr(order, "spare_part", None)
        if not spare_part and order.spare_parts:
            spare_part = order.spare_parts[0]

        if spare_part:
            spare_part.quantity = float(getattr(spare_part, "quantity", 0)) + int(getattr(order, "quantity", 1))
            spare_part.save()

        order.delete()
