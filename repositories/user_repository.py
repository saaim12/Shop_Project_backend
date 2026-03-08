from apps.users.models import User

class UserRepository:
    """Repository for User model operations."""
    
    @staticmethod
    def get_all_users(filters=None):
        queryset = User.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset
    
    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def create_user(data):
        return User.objects.create(**data)
    
    @staticmethod
    def update_user(user_id, data):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            for key, value in data.items():
                setattr(user, key, value)
            user.save()
        return user
    
    @staticmethod
    def delete_user(user_id):
        user = UserRepository.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False
