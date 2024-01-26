import factory
from django.contrib.auth.hashers import make_password
from factory.faker import faker

from api.models import Sensor, SensorData, User

FAKE = faker.Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("company_email")
    username = factory.Faker("user_name")
    company_name = factory.Faker("company")
    password = make_password("Password@123")


# from api.factory import UserFactory, SensorFactory, SensorDataFactory
#  x = SensorFactory.create_batch(10)
# x = SensorDataFactory.create_batch(10)
class SensorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Sensor

    operator = factory.SubFactory(UserFactory)
    name = factory.Faker(
        "random_element",
        elements=[
            "WeatherTracker",
            "MeteorSense",
            "ClimateProbe",
            "AtmosData",
            "SkyWatch",
            "AeroMetrix",
            "HumidiProbe",
            "BaroGuard",
            "PrecisioWeather",
            "CloudSense",
            "StormSense",
            "AeroPulse",
            "SolarClima",
        ],
    )
    description = factory.LazyAttribute(
        lambda x: f"A weather sensor for {x.operator.company_name} that captures and reports atmospheric conditions."
    )
    data_format = factory.Faker(
        "random_element", elements=["json, floats", "json,floats,text"]
    )
    communication_mode = factory.Faker(
        "random_element", elements=["wireless", "satellite"]
    )
    status = factory.Faker("random_element", elements=["passive", "active", "pending"])


class SensorDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SensorData

    sensor = factory.SubFactory(SensorFactory)
    temperature = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    humidity = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    atmospheric_pressure = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    wind_speed = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    wind_direction = factory.Faker(
        "random_element",
        elements=["EWS", "NWS", "NSE", "SWS", "SWE", "ENS", "SEN", "WSW"],
    )
    rainfall = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    weather_id = factory.Faker("pyint")
    main_weather = factory.Faker(
        "random_element",
        elements=["sunny", "cloudy", "rainy", "stormy", "foggy", "snowy"],
    )
    weather_description = factory.Faker(
        "random_element",
        elements=[
            "Today is sunny",
            "Today is cloudy",
            "Today is rainy",
            "Today is stormy",
            "Today is foggy",
            "Today is snowy",
        ],
    )
    temp_min = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    temp_max = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    sea_level_pressure = factory.Faker("pyint")
    ground_level_pressure = factory.Faker("pyint")
    wind_direction_deg = factory.Faker("pyint")
    wind_gust = factory.Faker("pyfloat", left_digits=2, right_digits=2)
    cloudiness_percentage = factory.Faker("pyint")
    visibility_distance = factory.Faker("pyint")
    city_id = factory.Faker("pyint")
    city_name = factory.Faker(
        "random_element",
        elements=[
            "New York City, USA",
            "Tokyo, Japan",
            "London, United Kingdom",
            "Paris, France",
            "Sydney, Australia",
            "Cape Town, South Africa",
            "Lagos, Nigeria",
            "Cairo, Egypt",
            "Rio de Janeiro, Brazil",
            "Mumbai, India",
            "Beijing, China",
            "Moscow, Russia",
            "Istanbul, Turkey",
            "Mexico City, Mexico",
            "Nairobi, Kenya",
            "Casablanca, Morocco",
            "Accra, Ghana",
        ],
    )
    http_response_code = 200


# import factory
# from factory.django import DjangoModelFactory
# from django.contrib.auth.hashers import make_password


# class UserFactory(DjangoModelFactory):
#     class Meta:
#         model = User
#         django_get_or_create = ('username', 'email', 'company_name', 'password')

#     email = factory.Faker('email')
#     username = factory.Faker('user_name')
#     company_name = factory.Faker('company')
#     password = make_password('Password@123')

#     @classmethod
#     def create_user(cls):
#         return cls.create()


#  password = factory.Faker('password', length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
