from __future__ import absolute_import, unicode_literals
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.messages import info, error
from django.shortcuts import reverse, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView, RedirectView
from django.views.generic.edit import FormView, View

from .forms import AddMenu, CustomizationEmployee, LoginClientForm, AddNewMeal, AddUser
from .models import Employee, Responsible, Meal, PlannedMenu, Profile
from .utils import send_msg_with_the_menu

import datetime
import logging
import pytz

logger = logging.Logger(__name__)


class LoginClientView(FormView):
    template_name = "./sign_in.html"
    form_class = LoginClientForm

    @never_cache  # Decorator to never get back to the form
    def dispatch(self, request, *args, **kwargs):
        """
        Function that will be executed  before the View login
        """
        return super(LogoutClientView, self).dispatch(request, *args, **kwargs)

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


class LogoutClientView(RedirectView):

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
        return super(LogoutClientView, self).dispatch(request, *args, **kwargs)


class DashboardResponsibleView(TemplateView):
    template_name = "./dashboard-responsible.html"

    def get_context_data(self, **kwargs):
        """
        prepare context for the dashboard responsible (all employees with their preferred meal and customizations)
        :param kwargs:
        :return: dict of all users
        """
        context = super(DashboardResponsibleView, self).get_context_data(**kwargs)
        responsible = Responsible.objects.get(user__pk=kwargs.get('user_id'))
        employees = Employee.objects.all()
        context['responsible'] = responsible
        context['employees'] = employees
        return context


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


class SubmitReminder(View):
    def post(self, request):
        """
        :param request: the request
        :return: msg with the status of the reminder
        """
        try:
            planned_menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
        except PlannedMenu.DoesNotExist:
            logger.error("Object doesn't exist, getting default menu")
            planned_menu = PlannedMenu.objects.all().first()

        message = 'You found Today menu flowing this link \n http://nora.cornershop.com/menu/%s' \
                  % planned_menu.uuid_menu
        response = send_msg_with_the_menu(message)
        msg = "Successfully sent it to Chilean employees in the slack channel" if response \
            else "Error sending reminder please try again or the admin will react"
        info(self.request, _(msg))
        return HttpResponseRedirect(reverse('dashboard-responsible', kwargs={
            'user_id': request.user.pk
        }))


class AddingMenuView(FormView):
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


class AddingUserView(FormView):
    template_name = "./add_new_user.html"
    form_class = AddUser

    def form_valid(self, form):
        """
        :param form:
        :return: create new user Admin side if user not found from email it will create a new one if every thing goes
        ok it will retrun a success msg into interface else error message
        """
        try:
            Profile.objects.get(form.cleaned_data.get('email'))
            error(self.request, 'User already exist with that email')
            return HttpResponseRedirect(reverse('add-user'))
        except :
            logger.info("User not found creating")
        if len(Responsible.objects.all()) > 0 and form.cleaned_data.get('is_responsible'):
            error(self.request, 'One responsible is allowed and already created')
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
            if form.cleaned_data.get('is_reponsible'):
                Responsible.objects.create(user=profile)
            if form.cleaned_data.get('is_employee'):
                Employee.objects.create(user=profile)

            info(self.request, 'User successfully created')
        except Exception as e:
            error(self.request, 'Error creating new user the error is %s' % e)
        return HttpResponseRedirect(reverse('add-user'))


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
        try:
            employee = Employee.objects.get(user__id=self.kwargs.get('user_id'))
            try:
                planned_menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
            except PlannedMenu.DoesNotExist:
                logger.error("Object doesn't exist, getting default menu")
                planned_menu = PlannedMenu.objects.all().first()
            return {'preferred_meal': employee.preferred_meal.pk if (employee.preferred_meal.pk
                                                                     and employee.preferred_meal
                                                                     in planned_menu.meals.all()) else '',
                    'customizations': employee.customizations
                    }
        except Exception as e:
            logger.error("Error in getting initial data %s" % e)
            return {'preferred_meal': '',
                    'customizations': ''
                    }

    def form_valid(self, form):
        """
        :param form:
        :return:
        """
        tz_clt = pytz.timezone('Chile/Continental')
        date_time_chile = datetime.datetime.now(tz_clt).strftime('%H:%M')
        if date_time_chile > '11:00':
            info(self.request, "Sorry but you can't choose your preferred meal after 11 AM (CLT)")
            return HttpResponseRedirect(reverse('dashboard-employee', kwargs={
                'user_id': self.request.user.pk
            }))
        print(form.cleaned_data)
        employee = self.get_object()
        print('preferred_meal' in form.cleaned_data.keys() and form.cleaned_data.get('preferred_meal'))
        if 'preferred_meal' in form.cleaned_data.keys() and form.cleaned_data.get('preferred_meal'):
            employee.preferred_meal = Meal.objects.get(pk=form.cleaned_data.get('preferred_meal'))
        if 'customizations' in form.cleaned_data.keys() and form.cleaned_data.get('customizations'):
            employee.customizations = form.cleaned_data.get('customizations')
        employee.save()
        return HttpResponseRedirect(reverse('dashboard-employee', kwargs={
            'user_id': self.request.user.pk
        }))

    def form_invalid(self, form):
        """
        :param form:
        :return:
        """
        print("invalid")
        print(form.cleaned_data)
        return HttpResponseRedirect(reverse('dashboard-employee', kwargs={
            'user_id': self.request.user.pk
        }))


class MenuDayView(TemplateView):
    template_name = "./menu_of_the_day.html"

    def get_context_data(self, **kwargs):
        """
        :param kwargs:
        :return:
        """
        context = super(MenuDayView, self).get_context_data(**kwargs)
        planned_menu = PlannedMenu.objects.get(uuid_menu=kwargs.get('uuid_menu'))
        context['menu_of_day'] = planned_menu
        return context


class AddMeal(FormView):

    form_class = AddNewMeal

    def form_valid(self, form):
        """
        :param form:
        :return:
        """
        print("valid form")
        print(form.cleaned_data)
        meal = Meal.objects.create(principal_meal=form.cleaned_data.get('principal_meal'),
                                   salad=form.cleaned_data.get('salad'),
                                   dessert=form.cleaned_data.get('dessert'))
        return redirect(reverse('add-menu'))

    def form_invalid(self, form):
        print("invalid form")
        print(form.cleaned_data)
        return HttpResponseRedirect(reverse('add-menu'))
