from apps.orders.models import Order

class OrderRepository:
    """Repository for Order model operations."""
    
    @staticmethod
    def get_all_orders(filters=None):
        queryset = Order.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @staticmethod
    def get_order_by_id(order_id):
        try:
            return Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return None
    
    @staticmethod
    def get_order_by_number(order_number):
        try:
            return Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            return None
    
    @staticmethod
    def create_order(data):
        return Order.objects.create(**data)
    
    @staticmethod
    def update_order(order_id, data):
        order = OrderRepository.get_order_by_id(order_id)
        if order:
            for key, value in data.items():
                setattr(order, key, value)
            order.save()
        return order
    
    @staticmethod
    def delete_order(order_id):
        order = OrderRepository.get_order_by_id(order_id)
        if order:
            order.delete()
            return True
        return False
