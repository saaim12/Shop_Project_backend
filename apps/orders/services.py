from bson import ObjectId

from apps.orders.models import Order
from apps.spare_parts.models import SparePart


class OrderService:
    @staticmethod
    def create_order(payload, customer):
        parts = []
        total_price = 0.0

        spare_part_ids = payload.get("spare_part_ids", [])
        if not spare_part_ids:
            raise ValueError("At least one spare part is required")

        for part_id in spare_part_ids:
            try:
                spare_part = SparePart.objects(id=ObjectId(part_id)).first()
            except Exception:
                spare_part = None

            if not spare_part:
                raise ValueError(f"Spare part not found: {part_id}")

            parts.append(spare_part)
            total_price += float(spare_part.price)

        order = Order(
            customer=customer,
            spare_parts=parts,
            total_price=total_price,
            status=Order.STATUS_PENDING,
        )
        order.save()
        return order

    @staticmethod
    def list_orders_for_user(user):
        if user.role in {"staff", "admin"}:
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
