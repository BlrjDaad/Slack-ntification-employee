# Simple account 

This project requires the design and implementation (using Django)
of a management system to coordinate the meal delivery for employees.

## Steps to go:
- Project requirement 
  
python 3.6, Django 2.2


- Create Slack APP:
1. create a new Slack App on api.slack.com.
2. Type in your app name.
3. Select the workspace you'd like to build your app on.
4. Navigate to OAuth & Permissions on the sidebar to add scopes to your app 
   (team:read, channels:manage, channels:read, chat:write, groups:write)
5. Install to workspace 
6. Copy the Bot User OAuth Access Token and paste it to settings SLACK_BOT_TOKEN
7. add the channel to settings CHANNEL_ID
- Install requirements 
  > pip3 install -r requirement.txt
  >
- Configure Postgres database by adding the parameters to env var as shown in example .envvar
- Excute 
  > python3 manage.py migrate
  >
- Execute a script to create admin user (Admin of app not of django)
from python shell (python3 manage.py shell)
  >from lunchapp.models import Profile
  > profile.objects.create(email="email@email.com", first_name="Admin",
  > last_name="Admin", phone="0033387538", country="Chile",
  > is_active=True, is_responsible=True, is_employee=True)
  > profile.set_password("123456789")
  > profile.save()
  > 
- Now go to the home page and then login page and log into Admin interface 
  when you can add one responsible and all employees