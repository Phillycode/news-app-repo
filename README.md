# YourNews - A News Application created with Django

This is my Django news application that uses bootstrap for a simple, clean user interface and includes a navbar for easy navigation between templates for all users.

## Admins - Important

Roles are assigned by django admin users or superusers. All users who register on the app first become readers. Readers can apply for a role via the navbar button. Once applied, an admin can review the application and if approved, the reader's role will change, they will lose their subscriptions (if any) and gain permissions and functions based on their new role. If the user's new role is a journalist or editor, the admin will also need to assign them to a Publisher. These options are cleanly presented to the admin from their dashboard from where they can review, approve and reject role applications.

## User functionality and permissions

- Readers: Can view approved articles, newsletters (don't need approval), and subscribe to journalists or publishers.
- Journalists: Full CRUD functionality for their articles and newsletters. Linked to a publisher by an admin upon role change.
- Editors: Are also linked to a publisher by an admin upon role change. They are responsible for approving or rejecting articles. Can view all articles and newsletters. They can edit and delete articles and newsletters from their Publisher only.
- Publishers: They have permissions to edit, view and delete articles/newsletters, but their webapp options are currently limited to only viewing. Their unique function is viewing their editors, journalists and other related stats such as subscriptions from their dashboard.
- Admins can currently have any role as normal in addition to being an admin. This makes testing easier, but can be modified for production.

## Run with Docker

- Ensure that docker is running
- Build the docker image:

```bash
docker build -t yournews .
```

- Run the container in the background:

```bash
docker run -d -p 8000:8000 --name yournews_container yournews
```

- Apply Django database migrations inside the running container:

```bash
docker exec -it yournews_container python manage.py migrate
```

- **Optional but recommended** — Create a Django superuser to manage role applications directly from the app’s Admin Dashboard via the navbar. While superusers can also access the Django admin panel at `http://localhost:8000/admin/`, all app functionality is available without using it.

```bash
docker exec -it yournews_container python manage.py createsuperuser
```

- Follow the prompts to set a username, email, and password.

- Once that is done, you can run the app by opening up your browser at `http://localhost:8000/`
- Feel free to test the app by creating users, applying for roles, and then approving them with the admin (superuser) account by navigating to the admin's dashboard.

### Note

When Django runs inside the container, it binds to `0.0.0.0:8000`, allowing it to accept connections from any network interface. However, from your host machine, you will need to access the site at `http://localhost:8000/`, since `0.0.0.0` is not accessible outside of the container.

### Additional info

For this project, the ALLOWED_HOSTS setting in settings.py is configured as:

```python
ALLOWED_HOSTS = ["*"]
```

This allows the application to run in any environment (including Docker Playground) without needing to change hostnames.

## Run without Docker (local setup)

- Check that you are using the desired database settings in settings.py (the default is already set as sqlite3 for development purposes).
- Create and activate a virtual environment (venv)
- Then install the dependencies from the included requirements.txt file. For my full requirements file (including dev tools), see requirements-dev.txt

```bash
pip install -r requirements.txt
```

- Apply database migrations.

```bash
python manage.py makemigrations
python manage.py migrate
```

- Create a Superuser in order to approve applications of users so that they can acquire new roles.

```bash
python manage.py createsuperuser
```

- Follow the prompts
- Once this is done, you can run the server

```
python manage.py runserver
```

- Open your browser at `http://127.0.0.1:8000`
- You can now register users and apply for roles
- With your admin/superuser, you can log into the news app and navigate to your Admin Dashboard from the Navbar.
- Here you can approve user applications and select a Publisher for them in the case of an Editor or Journalist.

## Emails

Emails are currently set up as file based for testing. They are sent following these actions:

- A user is approved or rejected for an applied role
- Readers are emailed articles (once approved) or newsletters (once submitted) if they are subscribed to the author (journalist) or corresponding publisher.
- Journalists are notified when their articles are approved and sent or when newsletters are sent out to subscribers successfully.
- Users request a password reset.

## API and Testing

- This application uses Django's RESTful API
- See yournews/TWITTER_SETUP.md for Twitter setup and testing instructions
- See yournews/API_README.md for API testing instructions

## References

My main source of information for this project was the HyperionDev course material and using the knowledge gained via my previous django projects. Below is a reference list on components and topics that I did additional research on for this particular project.

Bootstrap Navbar: https://getbootstrap.com/docs/5.3/components/navbar/
Bootstrap Modals: https://getbootstrap.com/docs/4.0/components/modal/
Django Widget tweaks for form control: https://pypi.org/project/django-widget-tweaks/
Django Signals: https://docs.djangoproject.com/en/5.2/topics/signals/
Using tweepy to authenticate with Twitter API V2 and posting tweets: https://docs.tweepy.org/en/stable/client.html#
Django REST framework: https://www.django-rest-framework.org/tutorial/quickstart/
Django admin commands that can be used via manage.py:

- https://docs.djangoproject.com/en/5.2/ref/django-admin/
- https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/

## Credits

Note: The images used in this application are referenced below and should be considered as placeholder images. They are not intended for commercial use.

Planet Earth icon obtained from: https://za.pinterest.com/pin/1109363320794867097/
Planet Banner obtained from: https://i.pinimg.com/1200x/90/ca/8d/90ca8d4313a3d2845ae390c0510bba09.jpg
Globe Footer image obtained from: https://i.pinimg.com/1200x/8c/50/53/8c505343cc2b05184638a366c9766772.jpg
