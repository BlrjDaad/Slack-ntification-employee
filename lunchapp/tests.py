from django.test import TestCase, Client
from .models import Employee, PlannedMenu, Profile, Meal, Responsible

import datetime
import uuid


class TestCaseProfile(TestCase):
    def setUp(self):
        # profile_admin
        Profile.objects.create(email='test_admin@gmail.com', first_name='test', last_name='test', phone='0096883933',
                               country='Chile', is_active=True, is_admin=True, is_responsible=False, is_employee=False)
        # profile_responsible
        Profile.objects.create(email='test_responsible@gmail.com', first_name='test', last_name='test',
                               phone='009688333', country='Brazil', is_active=True, is_admin=False, is_responsible=True,
                               is_employee=False)
        # profile_employee
        Profile.objects.create(email='test_employee@gmail.com', first_name='test', last_name='test',
                               phone='0096883934', country='Peru', is_active=True, is_admin=False,
                               is_responsible=False, is_employee=True)

    def test_profile_attributes(self):
        profile_admin = Profile.objects.get(email='test_admin@gmail.com')
        self.assertEqual(profile_admin.is_admin, True)
        self.assertEqual(profile_admin.is_active, True)
        self.assertEqual(profile_admin.country, 'Chile')
        profile_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        self.assertEqual(profile_responsible.is_admin, False)
        self.assertEqual(profile_responsible.is_active, True)
        self.assertEqual(profile_responsible.is_responsible, True)
        self.assertEqual(profile_responsible.country, 'Brazil')
        profile_employee = Profile.objects.get(email='test_employee@gmail.com')
        self.assertEqual(profile_employee.is_admin, False)
        self.assertEqual(profile_employee.is_active, True)
        self.assertEqual(profile_employee.is_responsible, False)
        self.assertEqual(profile_employee.is_employee, True)
        self.assertEqual(profile_employee.country, 'Peru')


class TestCaseResponsible(TestCase):

    def setUp(self):
        profile_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                     last_name='test', phone='009688333', country='Brazil',
                                                     is_active=True, is_admin=False, is_responsible=True,
                                                     is_employee=False)
        Responsible.objects.create(user=profile_responsible)

    def test_responsible_attributes(self):
        responsible = Responsible.objects.get(user__email='test_responsible@gmail.com')
        self.assertEqual(responsible.user.is_admin, False)
        self.assertEqual(responsible.user.is_active, True)
        self.assertEqual(responsible.user.is_responsible, True)
        self.assertEqual(responsible.user.country, 'Brazil')
        self.assertEqual(responsible.send_msg_with_the_menu("Test"), True)


class TestCaseEmployee(TestCase):
    def setUp(self):
        profile_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                                  last_name='test', phone='0096883934', country='Peru',
                                                  is_active=True, is_admin=False, is_responsible=False,
                                                  is_employee=True)
        employee = Employee.objects.create(user=profile_employee)
        meal = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        employee.customizations = 'no tomato in salad'
        employee.preferred_meal = meal
        employee.save()

    def test_employee_attributes(self):
        employee = Employee.objects.get(user__email='test_employee@gmail.com')
        self.assertEqual(employee.user.is_admin, False)
        self.assertEqual(employee.user.is_active, True)
        self.assertEqual(employee.user.is_responsible, False)
        self.assertEqual(employee.user.is_employee, True)
        self.assertEqual(employee.user.country, 'Peru')
        self.assertEqual(employee.preferred_meal.dessert, 'Lemon pie')
        self.assertEqual(employee.preferred_meal.salad, 'Green salad')
        self.assertEqual(employee.preferred_meal.principal_meal, 'Chicken')
        self.assertEqual(employee.customizations, 'no tomato in salad')


class TestCaseMeal(TestCase):
    def setUp(self):
        meal = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')

    def test_meal_attributes(self):
        meal = Meal.objects.get(principal_meal='Chicken')
        self.assertEqual(meal.dessert, 'Lemon pie')
        self.assertEqual(meal.salad, 'Green salad')
        self.assertEqual(meal.principal_meal, 'Chicken')


class TestCasePlannedMenu(TestCase):
    def setUp(self):
        meal_a = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        meal_b = Meal.objects.create(principal_meal='Corn pie', salad='Green salad', dessert='Brownies')
        meal_c = Meal.objects.create(principal_meal='Chicken Nugget Rice', salad='Cesar salad',
                                     dessert='chocolate mousse')
        meal_d = Meal.objects.create(principal_meal='Rice with hamburger', salad='Green salad',
                                     dessert='Fruit salad')
        today_menu = PlannedMenu.objects.create(planned_date=datetime.date.today())
        today_menu.meals.add(meal_a)
        today_menu.meals.add(meal_b)
        today_menu.meals.add(meal_c)
        today_menu.save()

    def test_meal_attributes(self):
        today_menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
        meal = Meal.objects.get(principal_meal='Rice with hamburger')
        self.assertEqual(today_menu.meals.all()[0].dessert, 'Lemon pie')
        self.assertEqual(today_menu.meals.all()[1].salad, 'Green salad')
        self.assertEqual(today_menu.meals.all()[2].principal_meal, 'Chicken Nugget Rice')
        self.assertEqual(meal in today_menu.meals.all(), False)


##########################
# Views test
##########################

class TestDashboardAdmin(TestCase):
    def setUp(self):
        user = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                      last_name='test', phone='0096883933', country='Chile', is_active=True,
                                      is_admin=True, is_responsible=False, is_employee=False)
        user.set_password('it is secret!')
        user.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0096083933', country='Chile', is_active=True,
                                                  is_admin=False, is_responsible=True, is_employee=False)
        user_responsible.set_password('it is secret!')
        user_responsible.save()
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()

    def test_functions(self):
        # Admin User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user.email, password='it is secret!')
        response = client.get('/dashboard/admin/%s/' % user.pk)
        self.assertEqual(response.status_code, 200)

        # Responsible User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is secret!')
        response = client.get('/dashboard/admin/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/admin/%s/' % user.pk)
        self.assertEqual(response.status_code, 302)

        # Employee User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client.login(username=user_responsible.email, password='it is employee!')
        response = client.get('/dashboard/admin/%s/' % user.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/admin/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/admin/%s/' % user_employee.pk)
        self.assertEqual(response.status_code, 302)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/dashboard/admin/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)


class TestAddUserAdmin(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()

    def test_functions(self):
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')

        # Admin user
        user_admin = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user_admin.email, password='it is secret!')
        response = client.get('/add_user/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 200)
        response_post = client.post('/add_user/%s/' % user_admin.pk, {'email': 'test@gmail.com',
                                                                      'first_name': 'user_name',
                                                                      'last_name': 'last_name_user',
                                                                      'phone': '00948485894',
                                                                      'country': 'Chile',
                                                                      'is_active': True,
                                                                      'is_responsible': False,
                                                                      'is_employee': True})
        self.assertEqual(response_post.status_code, 200)

        # Responsible profile
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_responsible.email, password='it is responsible!')
        response = client.get('/add_user/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/add_user/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/add_user/%s/' % user_admin.pk, {'email': 'test@gmail.com',
                                                                      'first_name': 'user_name',
                                                                      'last_name': 'last_name_user',
                                                                      'phone': '00948485894',
                                                                      'country': 'Chile',
                                                                      'is_active': True,
                                                                      'is_responsible': True,
                                                                      'is_employee': False})
        self.assertEqual(response_post.status_code, 302)
        response_post = client.post('/add_user/%s/' % user_responsible.pk, {'email': 'test@gmail.com',
                                                                            'first_name': 'user_name',
                                                                            'last_name': 'last_name_user',
                                                                            'phone': '00948485894',
                                                                            'country': 'Chile',
                                                                            'is_active': True,
                                                                            'is_responsible': True,
                                                                            'is_employee': False})
        self.assertEqual(response_post.status_code, 302)

        # Employee profile
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_employee.email, password='it is employee!')
        response = client.get('/add_user/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/add_user/%s/' % user_admin.pk, {'email': 'test@gmail.com',
                                                                      'first_name': 'user_name',
                                                                      'last_name': 'last_name_user',
                                                                      'phone': '00948485894',
                                                                      'country': 'Chile',
                                                                      'is_active': True,
                                                                      'is_responsible': True,
                                                                      'is_employee': False})
        self.assertEqual(response_post.status_code, 302)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/add_user/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/add_user/%s/' % user_admin.pk, {'email': 'test@gmail.com',
                                                                      'first_name': 'user_name',
                                                                      'last_name': 'last_name_user',
                                                                      'phone': '00948485894',
                                                                      'country': 'Chile',
                                                                      'is_active': True,
                                                                      'is_responsible': True,
                                                                      'is_employee': False})
        self.assertEqual(response_post.status_code, 302)


class TestDashboardResponsible(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        responsible = Responsible.objects.create(user=user_responsible)
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()

    def test_functions(self):
        # Admin User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user.email, password='it is secret!')
        response = client.get('/dashboard/responsible/%s/' % user.pk)
        self.assertEqual(response.status_code, 302)

        # Responsible User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is responsible!')
        response = client.get('/dashboard/responsible/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 200)
        response = client.get('/dashboard/responsible/%s/' % user.pk)
        self.assertEqual(response.status_code, 404)

        # Employee User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client.login(username=user_responsible.email, password='it is employee!')
        response = client.get('/dashboard/responsible/%s/' % user.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/responsible/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/responsible/%s/' % user_employee.pk)
        self.assertEqual(response.status_code, 302)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/dashboard/responsible/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)


class TestAddMenuResponsible(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        Responsible.objects.create(user=user_responsible)
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()
        Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        Meal.objects.create(principal_meal='Corn pie', salad='Green salad', dessert='Brownies')
        Meal.objects.create(principal_meal='Chicken Nugget Rice', salad='Cesar salad',
                            dessert='chocolate mousse')

    def test_functions(self):
        meals = Meal.objects.all()

        # Admin user
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_admin = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user_admin.email, password='it is secret!')
        response = client.get('/add_menu/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)

        # Responsible profile
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is responsible!')
        response = client.get('/add_menu/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 200)
        response_post = client.post('/add_menu/%s/' % user_responsible.pk, {'planned_date': datetime.date.today(),
                                                                            'meals': meals})
        self.assertEqual(response_post.status_code, 200)

        # Employee profile
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_employee.email, password='it is employee!')
        response = client.get('/add_menu/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/add_menu/%s/' % user_admin.pk, {'planned_date': datetime.date.today(),
                                                                      'meals': meals})
        self.assertEqual(response_post.status_code, 302)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/add_menu/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/add_menu/%s/' % user_admin.pk, {'planned_date': datetime.date.today(),
                                                                      'meals': meals})
        self.assertEqual(response_post.status_code, 302)


class TestAddMealResponsible(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        Responsible.objects.create(user=user_responsible)
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()

    def test_functions(self):
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')

        # Admin user
        user_admin = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user_admin.email, password='it is secret!')
        response_post = client.post('/add_meal/%s/' % user_admin.pk, {'principal_menu': 'Chicken',
                                                                      'salad': 'Green salad',
                                                                      'dessert': 'Lemon pie'
                                                                      })
        self.assertEqual(response_post.status_code, 302)  # redirect to login page

        # Responsible profile
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is responsible!')
        response_post = client.post('/add_meal/%s/' % user_responsible.pk,  {'principal_menu': 'Chicken',
                                                                             'salad': 'Green salad',
                                                                             'dessert': 'Lemon pie'
                                                                             })
        self.assertEqual(response_post.status_code, 302)  # redirect to menu page
        self.assertEqual(response_post.url, '/add_menu/%s/' % user_responsible.pk)  # redirect to menu page

        # Employee profile
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_employee.email, password='it is employee!')
        response_post = client.post('/add_meal/%s/' % user_responsible.pk,  {'principal_menu': 'Chicken',
                                                                             'salad': 'Green salad',
                                                                             'dessert': 'Lemon pie'
                                                                             })
        self.assertEqual(response_post.status_code, 302)  # redirect to login page

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response_post = client.post('/add_meal/%s/' % user_responsible.pk,  {'principal_menu': 'Chicken',
                                                                             'salad': 'Green salad',
                                                                             'dessert': 'Lemon pie'
                                                                             })
        self.assertEqual(response_post.status_code, 302)  # redirect to login page


class TestSubmitReminderResponsible(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        Responsible.objects.create(user=user_responsible)
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()
        Employee.objects.create(user=user_employee)
        meal_a = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        meal_b = Meal.objects.create(principal_meal='Corn pie', salad='Green salad', dessert='Brownies')
        meal_c = Meal.objects.create(principal_meal='Chicken Nugget Rice', salad='Cesar salad',
                                     dessert='chocolate mousse')

        today_menu = PlannedMenu.objects.create(planned_date=datetime.date.today())
        today_menu.meals.add(meal_a)
        today_menu.meals.add(meal_b)
        today_menu.meals.add(meal_c)
        today_menu.save()

    def test_functions(self):
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')

        # Admin user
        user_admin = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user_admin.email, password='it is secret!')
        response_post = client.post('/send_reminder/%s/' % user_admin.pk, {})
        self.assertEqual(response_post.status_code, 302)  # redirect to login page

        # Responsible profile
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is responsible!')
        response_post = client.post('/send_reminder/%s/' % user_responsible.pk)
        self.assertEqual(response_post.status_code, 302)  # redirect to dashboard responsible page
        self.assertEqual(response_post.url, '/dashboard/responsible/%s/' % user_responsible.pk)

        # Employee profile
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_employee.email, password='it is employee!')
        response_post = client.post('/send_reminder/%s/' % user_employee.pk, {})
        self.assertEqual(response_post.status_code, 302)  # redirect to login page

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response_post = client.post('/send_reminder/%s/' % user_admin.pk, {})
        self.assertEqual(response_post.status_code, 302)  # redirect to login page


class TestDashboardEmployee(TestCase):

    def setUp(self):
        user_admin = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                            last_name='test', phone='0096883933', country='Chile', is_active=True,
                                            is_admin=True, is_responsible=False, is_employee=False)
        user_admin.set_password('it is secret!')
        user_admin.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0094883933',
                                                  country='Chile', is_active=True, is_admin=False,
                                                  is_responsible=True, is_employee=False)
        user_responsible.set_password('it is responsible!')
        user_responsible.save()
        responsible = Responsible.objects.create(user=user_responsible)
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()
        Employee.objects.create(user=user_employee)
        meal_a = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        meal_b = Meal.objects.create(principal_meal='Corn pie', salad='Green salad', dessert='Brownies')
        meal_c = Meal.objects.create(principal_meal='Chicken Nugget Rice', salad='Cesar salad',
                                     dessert='chocolate mousse')

        today_menu = PlannedMenu.objects.create(planned_date=datetime.date.today())
        today_menu.meals.add(meal_a)
        today_menu.meals.add(meal_b)
        today_menu.meals.add(meal_c)
        today_menu.save()

    def test_functions(self):
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')

        # Admin user
        user_admin = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user_admin.email, password='it is secret!')
        response = client.get('/dashboard/employee/%s/' % user_admin.pk)
        menu = PlannedMenu.objects.get(planned_date=datetime.date.today())
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/dashboard/employee/%s/' % user_admin.pk, {'customizations': 'no tomato in salad',
                                                                                'preferred_meal': menu.meals.all()[0]})
        self.assertEqual(response_post.status_code, 302)

        # Responsible profile
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_responsible.email, password='it is responsible!')
        response = client.get('/dashboard/employee/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response = client.get('/dashboard/employee/%s/' % user_responsible.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/dashboard/employee/%s/' % user_responsible.pk,
                                    {'customizations': 'no tomato in salad',
                                     'preferred_meal': menu.meals.all()[0]})
        self.assertEqual(response_post.status_code, 302)

        # Employee profile
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        client.login(username=user_employee.email, password='it is employee!')
        response = client.get('/dashboard/employee/%s/' % user_employee.pk)
        self.assertEqual(response.status_code, 200)
        response_post = client.post('/dashboard/employee/%s/' % user_employee.pk,
                                    {'customizations': 'no tomato in salad',
                                     'preferred_meal': menu.meals.all()[0]})
        self.assertEqual(response_post.status_code, 200)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/dashboard/employee/%s/' % user_admin.pk)
        self.assertEqual(response.status_code, 302)
        response_post = client.post('/dashboard/employee/%s/' % user_admin.pk,
                                    {'customizations': 'no tomato in salad',
                                     'preferred_meal': menu.meals.all()[0]})
        self.assertEqual(response_post.status_code, 302)


class TestTodayMenu(TestCase):
    def setUp(self):
        user = Profile.objects.create(email='test_admin@gmail.com', first_name='test',
                                      last_name='test', phone='0096883933', country='Chile', is_active=True,
                                      is_admin=True, is_responsible=False, is_employee=False)
        user.set_password('it is secret!')
        user.save()
        user_responsible = Profile.objects.create(email='test_responsible@gmail.com', first_name='test',
                                                  last_name='test', phone='0096083933', country='Chile', is_active=True,
                                                  is_admin=False, is_responsible=True, is_employee=False)
        user_responsible.set_password('it is secret!')
        user_responsible.save()
        user_employee = Profile.objects.create(email='test_employee@gmail.com', first_name='test',
                                               last_name='test', phone='009004883933',
                                               country='Chile', is_active=True, is_admin=False,
                                               is_responsible=False, is_employee=True)
        user_employee.set_password('it is employee!')
        user_employee.save()
        meal_a = Meal.objects.create(principal_meal='Chicken', salad='Green salad', dessert='Lemon pie')
        meal_b = Meal.objects.create(principal_meal='Corn pie', salad='Green salad', dessert='Brownies')
        meal_c = Meal.objects.create(principal_meal='Chicken Nugget Rice', salad='Cesar salad',
                                     dessert='chocolate mousse')
        today_menu = PlannedMenu.objects.create(planned_date=datetime.date.today())
        today_menu.meals.add(meal_a)
        today_menu.meals.add(meal_b)
        today_menu.meals.add(meal_c)
        today_menu.save()

    def test_functions(self):
        menu = PlannedMenu.objects.get(planned_date=datetime.date.today())

        # Admin User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user = Profile.objects.get(email='test_admin@gmail.com')
        client.login(username=user.email, password='it is secret!')
        response = client.get('/menu/%s/' % menu.uuid_menu)
        self.assertEqual(response.status_code, 200)

        # Responsible User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_responsible = Profile.objects.get(email='test_responsible@gmail.com')
        client.login(username=user_responsible.email, password='it is secret!')
        response = client.get('/menu/%s/' % menu.uuid_menu)
        self.assertEqual(response.status_code, 200)

        # Employee User
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        user_employee = Profile.objects.get(email='test_employee@gmail.com')
        client.login(username=user_responsible.email, password='it is employee!')
        response = client.get('/menu/%s/' % menu.uuid_menu)
        self.assertEqual(response.status_code, 200)

        # AnonymousUser()
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/menu/%s/' % menu.uuid_menu)
        self.assertEqual(response.status_code, 200)

        # Menu not found
        client = Client(HTTP_USER_AGENT='Mozilla/5.0')
        response = client.get('/menu/%s/' % str(uuid.uuid4))
        self.assertEqual(response.status_code, 404)
