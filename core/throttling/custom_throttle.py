from rest_framework.throttling import SimpleRateThrottle, AnonRateThrottle, UserRateThrottle

class AnonRateThrottle(AnonRateThrottle):
    """
    Throttle rate for anonymous users.
    """
    scope = 'anon'

class UserRateThrottle(UserRateThrottle):
    """
    Throttle rate for authenticated users.
    """
    scope = 'user'

class BurstRateThrottle(SimpleRateThrottle):
    """
    Burst rate throttle for specific endpoints.
    """
    scope = 'burst'
