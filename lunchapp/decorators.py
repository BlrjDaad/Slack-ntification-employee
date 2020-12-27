from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def admin_user_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login/'):
    """
    Decorator for views that checks that the user is logged in and is a admin user,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_active and u.is_admin,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def responsible_user_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login/'):
    """
    Decorator for views that checks that the user is logged in and is a employee user,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_active and u.is_responsible,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def employee_user_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='/login/'):
    """
    Decorator for views that checks that the user is logged in and is a employee user,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_active and u.is_employee,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator
