# Status Constants
class OrderStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

class AppointmentStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
    ]

class PaymentStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    
    CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

# Vehicle Constants
class VehicleType:
    SEDAN = 'sedan'
    SUV = 'suv'
    TRUCK = 'truck'
    VAN = 'van'
    COUPE = 'coupe'
    HATCHBACK = 'hatchback'
    
    CHOICES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (TRUCK, 'Truck'),
        (VAN, 'Van'),
        (COUPE, 'Coupe'),
        (HATCHBACK, 'Hatchback'),
    ]

class FuelType:
    PETROL = 'petrol'
    DIESEL = 'diesel'
    ELECTRIC = 'electric'
    HYBRID = 'hybrid'
    
    CHOICES = [
        (PETROL, 'Petrol'),
        (DIESEL, 'Diesel'),
        (ELECTRIC, 'Electric'),
        (HYBRID, 'Hybrid'),
    ]
