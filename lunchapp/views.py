from __future__ import absolute_import, unicode_literals
from django.contrib.auth import login as auth_login
from django.contrib.messages import info
from django.shortcuts import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from .forms import LoginClientForm


class LoginUserMixin(FormView):
    template_name = ""

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        return super(LoginUserMixin, self).dispatch(request, *args, **kwargs)


class LoginClientView(LoginUserMixin):
    template_name = "./signin.html"
    form_class = LoginClientForm

    def form_valid(self, form):
        user = form.get_user()
        auth_login(self.request, user)
        info(self.request, _("Welcome to your Cornershop account"))
        print(user.is_responsible)
        if user.is_responsible:
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


class DashboardResponsibleView(TemplateView):
    template_name = "./dashboard-responsible.html"


class DashboardEmployeeView(TemplateView):
    template_name = "./dashboard-employee.html"

