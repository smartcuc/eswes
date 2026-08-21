from decimal import Decimal
from datetime import datetime, date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from devices.models import Home
from producer.models import GeneratorSystem, GeneratorString, GeneratorType, Orientation
from forecast.models import WeatherForecast, SolarForecast
from forecast.services_weather import store_weather_payload_for_home
from forecast.services_physics import predict_next_24h_physics_for_generator_string
from forecast.services_forecast_accuracy import calculate_forecast_accuracy

User = get_user_model()


class ForecastServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="forecasttestuser",
            email="forecast@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Solar Home",
            latitude=50.9375,
            longitude=6.9603,
        )
        self.gen_type = GeneratorType.objects.create(key="pv", name="Photovoltaik")
        self.orientation = Orientation.objects.create(
            key="south",
            name="Süd",
            azimuth_deg=180,
        )
        self.generator = GeneratorSystem.objects.create(
            home=self.home,
            name="Dachanlage",
            generator_type=self.gen_type,
            peak_power_kw=Decimal("10.0"),
        )
        self.string = GeneratorString.objects.create(
            generator=self.generator,
            name="String 1",
            peak_power_kwp=Decimal("5.0"),
            orientation=self.orientation,
            tilt_deg=35,
            shading_percent=Decimal("0.0"),
        )

    def test_store_weather_payload_for_home(self):
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        timestamps = [(now + timedelta(hours=i)).isoformat() for i in range(24)]
        payload = {
            "timestamps": timestamps,
            "radiation": [500.0] * 24,
            "temperature": [20.0] * 24,
            "cloud_cover": [10.0] * 24,
        }

        result = store_weather_payload_for_home(self.home, payload)
        self.assertEqual(result["written"], 24)
        self.assertEqual(result["skipped"], 0)

        count = WeatherForecast.objects.filter(home=self.home).count()
        self.assertEqual(count, 24)

    def test_predict_next_24h_physics_for_generator_string(self):
        base_now = timezone.now()
        # Store weather forecast first
        weather_objs = [
            WeatherForecast(
                home=self.home,
                ts=base_now + timedelta(hours=i),
                temperature_c=22.0,
                cloud_cover_pct=0.0,
                shortwave_radiation_wm2=800.0,
            )
            for i in range(24)
        ]
        WeatherForecast.objects.bulk_create(weather_objs)

        physics_preds = predict_next_24h_physics_for_generator_string(self.string)
        self.assertGreaterEqual(len(physics_preds), 1)
        self.assertIn("forecast_kw", physics_preds[0])
        self.assertGreater(physics_preds[0]["forecast_kw"], 0)

