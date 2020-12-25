"""backend_test_bellarej URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from lunchapp.views import LoginClientView, LogoutClientView, DashboardEmployeeView,\
    DashboardResponsibleView, AddingMenuView, MenuDayView, SubmitReminder, AddMeal, DashboardAdminView, AddingUserView

urlpatterns = [
    url(r'^login/$', LoginClientView.as_view(), name='login'),
    url(r'^logout/$', LogoutClientView.as_view(), name='logout'),
    url(r'^send_reminder/$', SubmitReminder.as_view(), name='send_reminder'),
    url(r'^dashboard/admin/(?P<user_id>[0-9]+)/$', DashboardAdminView.as_view(),
        name='dashboard-admin'),
    url(r'^dashboard/responsible/(?P<user_id>[0-9]+)/$', DashboardResponsibleView.as_view(),
        name='dashboard-responsible'),
    url(r'^dashboard/employee/(?P<user_id>[0-9]+)/$', DashboardEmployeeView.as_view(),
        name='dashboard-employee'),
    url(r'^add_menu/$', AddingMenuView.as_view(),
        name='add-menu'),
    url(r'^add_user/$', AddingUserView.as_view(),
        name='add-user'),
    url(r'^add_meal/$', AddMeal.as_view(),
        name='add-meal'),
    url(r'^menu/(?P<uuid_menu>[0-9A-Za-z_\-]+)/$', MenuDayView.as_view(),
        name='menu_of_the_day'),
]
