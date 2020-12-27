from __future__ import absolute_import, unicode_literals

from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.messages import error, info
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView, View

from .decorators import admin_user_required, employee_user_required, responsible_user_required
from .forms import AddMenu, AddNewMeal, AddUser, CustomizationEmployee, LoginClientForm
from .models import Employee, Responsible, Meal, PlannedMenu, Profile
from .utils import invite_to_channel

import datetime
import logging
import pytz

logger = logging.Logger(__name__)


class HomeView(TemplateView):
    template_name = './home_page.html'


class LoginView(FormView):
    template_name = "./sign_in.html"
    form_class = LoginClientForm

    @never_cache  # Decorator to never get back to the form
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login
        """
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        :param form: the form class of login user (admin, responsible or employee)
        :return: the dashboard of the connected user if user is authenticated else invalid login
        """
        user = form.get_user()
        auth_login(self.request, user)
        info(self.request, _("Welcome to your Cornershop account"))
        if user.is_admin:
            index_path = reverse('dashboard-admin', kwargs={
                'user_id': user.pk
            })
            response = HttpResponseRedirect(index_path)
        elif user.is_responsible:
            index_path = reverse('dashboard-responsible', kwargs={
                'user_id': user.pk
            })
            response = HttpResponseRedirect(index_path)
        else:
            index_path = reverse('dashboard-employee', kwargs={
                'user_id': user.pk
            })
            response = HttpResponseRedirect(index_path)
        return response


class LogoutView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        """
        log out client and redirect to login interface
        """
        auth_logout(self.request)
        info(self.request,
             _("Your Are disconnected from Cornershop."))
        return reverse('login')

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login
        """
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class DashboardAdminView(TemplateView):
    template_name = "./dashboard-admin.html"

    def get_context_data(self, **kwargs):
        """
        prepare context for the dashboard admin (all users)
        :param kwargs:
        :return: dict with all profiles
        """
        context = super(DashboardAdminView, self).get_context_data(**kwargs)
        profiles = Profile.objects.all()
        context['profiles'] = profiles
        return context

    @method_decorator(admin_user_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login in this view it will check if
        the user is authenticated and responsible
        """
        super(DashboardAdminView, self).dispatch(request, *args, **kwargs)
        connected_profile = get_object_or_404(Profile, pk=self.kwargs.get('user_id'))
        if not connected_profile.is_admin:
            logger.error('User not allowed user.email %s' % request.user.email)
            return HttpResponseForbidden('<h1>Forbidden</h1>')
        return super(DashboardAdminView, self).dispatch(request, *args, **kwargs)


class AddingUserView(FormView):
    template_name = "./add_new_user.html"
    form_class = AddUser

    def form_valid(self, form):
        """
        :param form:
        :return: create new user Admin side if user not found from email it will create a new one if every thing goes
        ok it will return a success msg into interface else error message
        """
        try:
            Profile.objects.get(form.cleaned_data.get('email'))
            error(self.request, 'User already exist with that email')
            return HttpResponseRedirect(reverse('add-user', kwargs={
                'user_id': self.request.user.pk
            }))
        except Exception as e:
            logger.info("User not found creating...")

        if len(Responsible.objects.all()) > 0 and form.cleaned_data.get('is_responsible'):
            error(self.request, 'One responsible is allowed and he is already created')
            return HttpResponseRedirect(reverse('add-user'))
        try:
            profile = Profile.objects.create(email=form.cleaned_data.get('email'),
                                             first_name=form.cleaned_data.get('first_name'),
                                             last_name=form.cleaned_data.get('last_name'),
                                             phone=form.cleaned_data.get('phone'),
                                             country=form.cleaned_data.get('country'),
                                             is_active=form.cleaned_data.get('is_active'),
                                             is_responsible=form.cleaned_data.get('is_responsible'),
                                             is_employee=form.cleaned_data.get('is_employee'))
            if form.cleaned_data.get('is_responsible'):
                Responsible.objects.create(user=profile)
            if form.cleaned_data.get('is_employee'):
                Employee.objects.create(user=profile)
            info(self.request, 'User successfully created')
            # Only employee from Chile are invited to slack channel of the menu notifier
            if profile.country == 'Chile':
                invite_to_channel(profile.email)

        except Exception as e:
            error(self.request, 'Error creating new user the error is %s' % e)
        return HttpResponseRedirect(reverse('add-user',  kwargs={
            'user_id': self.request.user.pk
        }))

    @method_decorator(admin_user_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login in this view it will check if
        the user is authenticated and responsible
        """
        super(AddingUserView, self).dispatch(request, *args, **kwargs)
        connected_profile = get_object_or_404(Profile, pk=kwargs.get('user_id'))
        if not connected_profile.is_admin:
            logger.error('User not allowed user.email %s' % request.user.email)
            return HttpResponseForbidden('<h1>Forbidden</h1>')
        return super(AddingUserView, self).dispatch(request, *args, **kwargs)


class LoginRequiredResponsible(View):

    @method_decorator(responsible_user_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login in this view it will check if
        the user is authenticated and responsible
        """
        super(LoginRequiredResponsible, self).dispatch(request, *args, **kwargs)
        connected_profile = get_object_or_404(Responsible, user=request.user)
        if not connected_profile.user.is_responsible:
            logger.error('User not allowed user.email %s' % request.user.email)
            return HttpResponseForbidden('<h1>Forbidden</h1>')
        return super(LoginRequiredResponsible, self).dispatch(request, *args, **kwargs)


class DashboardResponsibleView(LoginRequiredResponsible, TemplateView):
    template_name = "./dashboard-responsible.html"

    def get_context_data(self, **kwargs):
        """
        prepare context for the dashboard responsible (all employees with their preferred meal and customizations)
        :param kwargs:
        :return: dict of all users
        """
        context = super(DashboardResponsibleView, self).get_context_data(**kwargs)
        responsible = get_object_or_404(Responsible, user__pk=kwargs.get('user_id'))
        employees = Employee.objects.all()
        context['responsible'] = responsible
        context['employees'] = employees
        return context


class SubmitReminder(LoginRequiredResponsible):

    def post(self, request, *args, **kwargs):
        """
        :param request: the request
        :return: msg with the status of the reminder
        """
        responsible = get_object_or_404(Responsible, user=request.user)
        try:
            planned_menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
        except PlannedMenu.DoesNotExist:
            logger.error("Object doesn't exist, getting default menu")
            planned_menu = PlannedMenu.objects.all().first()

        message = 'You found Today menu flowing this link \n http://nora.cornershop.com/menu/%s' \
                  % planned_menu.uuid_menu
        response = responsible.send_msg_with_the_menu(message)
        msg = "Successfully sent it to Chilean employees in the slack channel" if response \
            else "Error sending reminder please try again or the admin will react"
        info(self.request, _(msg))
        return HttpResponseRedirect(reverse('dashboard-responsible', kwargs={
            'user_id': request.user.pk
        }))


class AddingMenuView(LoginRequiredResponsible, FormView):
    template_name = "./add_new_menu.html"
    form_class = AddMenu

    def get_context_data(self, **kwargs):
        """
        :param kwargs:
        :return: dict with adding new meal to menu
        """
        context = super(AddingMenuView, self).get_context_data(**kwargs)
        context['form_new_meal'] = AddNewMeal()
        return context

    def form_valid(self, form):
        """
        :param form:
        :return: create the menu of the day
        """
        planned_menu = PlannedMenu.objects.create(planned_date=form.cleaned_data.get('planned_date'))
        for meal_id in form.cleaned_data.get('meals'):
            meal = Meal.objects.get(pk=meal_id)
            if meal:
                planned_menu.meals.add(meal)
            else:
                continue
        planned_menu.save()
        return HttpResponseRedirect(reverse('menu_of_the_day', kwargs={'uuid_menu': planned_menu.uuid_menu}))


class AddMeal(LoginRequiredResponsible, FormView):
    template_name = ""
    form_class = AddNewMeal

    def form_valid(self, form):
        """
        function to add new meal to the meals option it will return a msg with the creation's status
        :param form: the form of creating new meal
        :return:
        """
        try:
            Meal.objects.create(principal_meal=form.cleaned_data.get('principal_meal'),
                                salad=form.cleaned_data.get('salad'),
                                dessert=form.cleaned_data.get('dessert'))
            info(self.request, 'New meal created, please refresh to get it in menu')
        except Exception as e:
            error(self.request, 'Error in creating meal %s' % e)
        return redirect(reverse('add-menu', kwargs={'user_id': self.request.user.pk}))


class DashboardEmployeeView(FormView):
    template_name = "./dashboard-employee.html"
    form_class = CustomizationEmployee

    def get_object(self):
        """
        :return: the connected employee object
        """
        employee = get_object_or_404(Employee, user=self.request.user)
        return employee

    def get_initial(self):
        """
        :return: the detail of the connected employee into form to edit
        """
        employee = self.get_object()
        try:
            planned_menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
            preferred_meal = employee.preferred_meal.pk if (employee.preferred_meal.pk
                                                            and employee.preferred_meal
                                                            in planned_menu.meals.all()) else ''
            customizations = employee.customizations
        except PlannedMenu.DoesNotExist:
            logger.error("Object doesn't exist, getting default menu")
            planned_menu = PlannedMenu.objects.all().first()
            preferred_meal = employee.preferred_meal.pk if (employee.preferred_meal.pk
                                                            and employee.preferred_meal
                                                            in planned_menu.meals.all()) else ''
            customizations = employee.customizations

        except:
            preferred_meal = customizations = ''

        return {'preferred_meal': preferred_meal,
                'customizations': customizations
                }

    def form_valid(self, form):
        """
        :param form: the form of choosing custom meal of to indicate some customizations
        :return: the same view but with the new customizations indicated by the user if time didn't pass 11 AM CLT
         else nothing will be saved and msg will be return
        """
        tz_clt = pytz.timezone('Chile/Continental')
        date_time_chile = datetime.datetime.now(tz_clt).strftime('%H:%M')
        if date_time_chile > '11:00':
            info(self.request, "Sorry but you can't choose your preferred meal after 11 AM (CLT)")
            return HttpResponseRedirect(reverse('dashboard-employee', kwargs={
                'user_id': self.request.user.pk
            }))
        employee = self.get_object()
        if 'preferred_meal' in form.cleaned_data.keys() and form.cleaned_data.get('preferred_meal'):
            employee.preferred_meal = Meal.objects.get(pk=form.cleaned_data.get('preferred_meal'))
        if 'customizations' in form.cleaned_data.keys() and form.cleaned_data.get('customizations'):
            employee.customizations = form.cleaned_data.get('customizations')
        employee.save()
        return HttpResponseRedirect(reverse('dashboard-employee', kwargs={
            'user_id': self.request.user.pk
        }))

    @method_decorator(employee_user_required)
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login in this view it will check if
        the user is authenticated and employee
        """
        super(DashboardEmployeeView, self).dispatch(request, *args, **kwargs)
        connected_profile = get_object_or_404(Employee, user=request.user)
        if not connected_profile.user.is_employee:
            logger.error('User not allowed user.email %s' % request.user.email)
            return HttpResponseForbidden('<h1>Forbidden</h1>')
        return super(DashboardEmployeeView, self).dispatch(request, *args, **kwargs)


class MenuDayView(TemplateView):
    template_name = "./menu_of_the_day.html"

    def get_context_data(self, **kwargs):
        """
        :param kwargs: contains uuid of the menu
        :return: Context of the public page with the menu of the day
        """
        context = super(MenuDayView, self).get_context_data(**kwargs)
        planned_menu = get_object_or_404(PlannedMenu, uuid_menu=kwargs.get('uuid_menu'))
        context['menu_of_day'] = planned_menu
        return context
