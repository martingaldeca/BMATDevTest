from django.contrib.auth.models import User
from factory import Faker, PostGenerationMethodCall
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = FuzzyText()
    password = PostGenerationMethodCall('set_password', 'adm1n')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_staff = False
    is_active = True
    is_superuser = False
