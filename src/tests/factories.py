import factory
from faker import Faker

from app.core.security import get_password_hash
from app.models import User, SurveyAttribute, Survey, AnswerAttribute, Answer

fake = Faker()


def slugify(to_slugify: str) -> str:
    return to_slugify.replace(" ", "_").lower()


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda object_: slugify(fake.name()))
    email = factory.LazyAttribute(lambda object_: f"{slugify(fake.name())}@{fake.free_email_domain()}")
    password = factory.LazyAttribute(lambda object_: get_password_hash(fake.password()))
    first_name = factory.LazyAttribute(lambda object_: fake.first_name())
    last_name = factory.LazyAttribute(lambda object_: fake.last_name())
    birth_date = factory.LazyAttribute(lambda object_: fake.date_of_birth())
    is_active = factory.LazyAttribute(lambda object_: fake.pybool())
    is_stuff = factory.LazyAttribute(lambda object_: fake.pybool())
    is_superuser = factory.LazyAttribute(lambda object_: fake.pybool())


class SurveyAttributeFactory(factory.Factory):
    class Meta:
        model = SurveyAttribute

    available = factory.LazyAttribute(lambda object_: fake.pybool())
    question = factory.LazyAttribute(lambda object_: fake.sentence())
    required = factory.LazyAttribute(lambda object_: fake.pybool())


class SurveyFactory(factory.Factory):
    class Meta:
        model = Survey

    name = factory.LazyAttribute(lambda object_: fake.name())
    available = factory.LazyAttribute(lambda object_: fake.pybool())
    description = factory.LazyAttribute(lambda object_: fake.text())


class AnswerAttributeFactory(factory.Factory):
    class Meta:
        model = AnswerAttribute

    text = factory.LazyAttribute(lambda object_: fake.text())


class AnswerFactory(factory.Factory):
    available = factory.LazyAttribute(lambda object_: fake.pybool())

    class Meta:
        model = Answer
