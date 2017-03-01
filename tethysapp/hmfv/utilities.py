
def user_permission_test(user):
    return user.is_superuser or user.is_staff