from apps.vehicles.models import Vehicle

class VehicleRepository:
    """Repository for Vehicle model operations."""
    
    @staticmethod
    def get_all_vehicles(filters=None):
        queryset = Vehicle.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        try:
            return Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            return None
    
    @staticmethod
    def get_vehicle_by_vin(vin):
        try:
            return Vehicle.objects.get(vin=vin)
        except Vehicle.DoesNotExist:
            return None
    
    @staticmethod
    def create_vehicle(data):
        return Vehicle.objects.create(**data)
    
    @staticmethod
    def update_vehicle(vehicle_id, data):
        vehicle = VehicleRepository.get_vehicle_by_id(vehicle_id)
        if vehicle:
            for key, value in data.items():
                setattr(vehicle, key, value)
            vehicle.save()
        return vehicle
    
    @staticmethod
    def delete_vehicle(vehicle_id):
        vehicle = VehicleRepository.get_vehicle_by_id(vehicle_id)
        if vehicle:
            vehicle.delete()
            return True
        return False
