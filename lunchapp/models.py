from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .constants import COUNTRY, LANG_TYPE
from .utils import send_msg_with_the_menu

import datetime
import uuid


class Profile(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        max_length=255,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name=_("First name"),
        max_length=50,
        help_text=_("Enter the first name"),
        null=True,
        blank=True
    )
    last_name = models.CharField(
        verbose_name=_("Last name"),
        max_length=50,
        help_text=_("Enter the last name"),
        null=True,
        blank=True
    )
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=50,
        choices=LANG_TYPE,
        default=LANG_TYPE[0][0],
        help_text=_('Choose your preferred language'),
    )
    phone = models.CharField(
        verbose_name=_("Phone number"),
        max_length=50,
        help_text=_("Enter the phone number"),
        null=True,
        blank=True,
        unique=True
    )
    country = models.CharField(
        verbose_name=_("Country"),
        max_length=255,
        help_text=_("Choose the country of the employee"),
        choices=COUNTRY,
        default=COUNTRY[0][0]
    )
    is_active = models.BooleanField(default=False)
    is_responsible = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    objects = UserManager()


class Meal(models.Model):
    principal_meal = models.CharField(
        verbose_name=_('the principal meal'),
        max_length=255,
        help_text=_('Enter the name of the principal meal'),
    )
    salad = models.CharField(
        verbose_name=_('salad'),
        max_length=255,
        help_text=_('Enter the name of the salad'),)
    dessert = models.CharField(
        verbose_name=_('dessert'),
        max_length=255,
        help_text=_('Enter the name of the dessert'),)


class PlannedMenu(models.Model):
        planned_date = models.DateField(_('date joined'), default=timezone.now)
        meals = models.ManyToManyField(Meal)


class Responsible(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)

    def send_slack_reminder(self):
        today_menu = PlannedMenu.objects.get(planned_date=
                                             datetime.datetime.now().strftime("%d/%M/%Y"))
        # TODO send msg only for chilean employees
        send_msg_with_the_menu(today_menu.id)


class Employee(models.Model):
    uuid = models.CharField(
        verbose_name=_('UUID Employee'),
        blank=False,
        null=False,
        editable=False,
        max_length=50,
        default=str(uuid.uuid4())
    )
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    preferred_meal = models.OneToOneField(Meal, null=True, on_delete=models.PROTECT)
