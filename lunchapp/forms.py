from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

from .constants import COUNTRY
from .models import Employee, Meal, Profile, PlannedMenu

import datetime


class LoginClientForm(AuthenticationForm):
    """
    A custom authentication form used in the Client.
    """
    username = forms.EmailField(
        label=_("E-mail"),
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-white',
            'placeholder': 'email@yourhostname.com',
        })
    )

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-white',
            'placeholder': _('Password'),
        })
    )
    error_messages = {
        'invalid_login': _("Please enter the correct %(username)s and password "
                           "for business account. Note that both fields may be "
                           "case-sensitive."),
    }
    required_css_class = 'required'

    def confirm_login_allowed(self, user):
        """
        :param user:
        :return:
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )

    class Meta:
        model = Profile
        fields = ('username', 'password')


class AddUser(forms.ModelForm):
    email = forms.CharField(
        label=_("E-mail Address"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-white email',
            'placeholder': 'email@yourhostname.co.uk',
        }),
    )
    first_name = forms.CharField(
        label=_("First name"),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-white cpy-name',
            'placeholder': _('First name'),
            'aria-required': 'true'
        })
    )
    last_name = forms.CharField(
        label=_("last name"),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-white cpy-name',
            'placeholder': _('Last Name'),
            'aria-required': 'true'
        })
    )
    phone = forms.CharField(
        label=_("Phone"),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-white',
            'placeholder': '(033) 123-456 78',
            'aria-required': 'true',
            'data-mask': '(999) 999-9999 x9999'
        })
    )
    country = forms.ChoiceField(
        label=_("Country"),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control form-white',
            'placeholder': _('Country'),
            'aria-required': 'true'
        }),
        initial=COUNTRY[0][1],
        choices=COUNTRY
    )
    is_active = forms.BooleanField(
        label=_("is_active"),
        required=False
    )
    is_responsible = forms.BooleanField(
        label=_("is_responsible"),
        required=False
    )
    is_employee = forms.BooleanField(
        label=_("is_employee"),
        required=False
    )

    class Meta:
        model = Profile
        fields = ('email', 'first_name', 'last_name', 'phone', 'country', 'is_active', 'is_responsible', 'is_employee')


class AddMenu(forms.ModelForm):
    choices = [(meal.pk, (meal.principal_meal + ', ' + meal.salad + ', ' + meal.dessert)) for meal in Meal.objects.all()]
    planned_date = forms.DateInput(attrs={
        'required': 'required',
        'class': 'datepicker'
    })
    meals = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={
            'required': 'required',
            'class': 'selectpicker'
        }),
        choices=choices
    )

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        self.planned_date = datetime.date.today()
        super(AddMenu, self).__init__(*args, **kwargs)

    class Meta:
        model = PlannedMenu
        fields = ('planned_date', 'meals')


class CustomizationEmployee(forms.ModelForm):
    choices = [(meal.pk, (meal.principal_meal + ', ' + meal.salad + ', ' + meal.dessert)) for meal in Meal.objects.all()]
    choices.insert(0, (None, 'No meal preferred'))
    customizations = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-white',
                'placeholder': 'your customizations'
            })
    )
    preferred_meal = forms.ChoiceField(
        label=_('preferred meal'),
        required=False,
        choices=choices,
        widget=forms.Select(attrs={
            'class': 'form-control form-white'
        })
    )

    def __init__(self, *args, **kwargs):
        # Get initial data passed from the view
        """
        :param args:
        :param kwargs:
        """
        if 'preferred_meal' in kwargs.get('initial') and kwargs.get('initial', {}).get('preferred_meal'):
            self.preferred_meal = kwargs.get('initial').get('preferred_meal')
        if 'customizations' in kwargs.get('initial') and kwargs.get('initial', {}).get('customizations'):
            self.customizations = kwargs.get('initial').get('customizations')
        super(CustomizationEmployee, self).__init__(*args, **kwargs)

    class Meta:
        model = Employee
        fields = ('customizations', 'preferred_meal')


class AddNewMeal(forms.ModelForm):
    principal_meal = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-white',
                'placeholder': 'principal meal'
            })
    )
    salad = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-white',
                'placeholder': 'salad'
            })
    )
    dessert = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-white',
                'placeholder': 'dessert'
            })
    )

    class Meta:
        model = Meal
        fields = ('principal_meal', 'salad', 'dessert')
