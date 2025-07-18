#! /usr/bin/env bash

set -o errexit   #  exit on error

pip install -r requirement.txt

python manage.py collectstatic --no-input
python manage.py makemigrations user
python manage.py makemigrations post
python manage.py makemigrations chat
python manage.py migrate

# Create superuser
python manage.py shell << END
from django.contrib.auth import get_user_model
import os

User = get_user_model()
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "femiduyile@gmail.com")
username = os.getenv("DJANGO_SUPERUSER_USERNAME", "Darlingtin")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "bavtwany")

if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print("Superuser created")
else:
    print("Superuser already exists")
END