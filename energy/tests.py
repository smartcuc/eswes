from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from energy.flow_engine import calculate_energy_flow
from energy.services.sankey import build_live_sankey
from energy.ems.services import build_device_signals
from energy.models import EMSSignalType, EMSSignalSource
from devices.models import Home, Device, DeviceConfig, DeviceRole, MetricDefinition

User = get_user_model()


class EnergyFlowEngineTest(TestCase):
    def test_calculate_energy_flow_basic(self):
        signals = {
            "pv": {"production": 5000},
            "battery": {"charge": 1000, "discharge": 0},
            "grid": {"import": 500, "export": 0},
            "load": {"consumption": 4500},
        }
        flow = calculate_energy_flow(signals)

        self.assertIn("pv_to_load", flow)
        self.assertIn("pv_to_battery", flow)
        self.assertIn("pv_to_grid", flow)
        self.assertIn("battery_to_load", flow)
        self.assertIn("grid_to_load", flow)

    def test_calculate_energy_flow_empty(self):
        flow = calculate_energy_flow({})
        self.assertEqual(flow["pv_to_load"], 0)
        self.assertEqual(flow["pv_to_battery"], 0)
        self.assertEqual(flow["pv_to_grid"], 0)
        self.assertEqual(flow["battery_to_load"], 0)
        self.assertEqual(flow["grid_to_load"], 0)


class EMSSignalServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testenergyuser",
            email="energy@example.com",
            password="testpassword123",
        )
        self.home = Home.objects.create(
            user=self.user,
            name="Test Home",
        )
        self.signal_pv = EMSSignalType.objects.create(key="pv", label="PV")
        self.signal_grid = EMSSignalType.objects.create(key="grid", label="Grid")

        self.pv_device = Device.objects.create(
            home=self.home,
            identifier="pv_inverter_1",
            configured=True,
        )
        self.grid_device = Device.objects.create(
            home=self.home,
            identifier="grid_meter_1",
            configured=True,
        )

        EMSSignalSource.objects.create(
            home=self.home,
            device=self.pv_device,
            signal_type=self.signal_pv,
        )
        EMSSignalSource.objects.create(
            home=self.home,
            device=self.grid_device,
            signal_type=self.signal_grid,
        )

    def test_build_device_signals_empty_cache(self):
        signals = build_device_signals(self.user)
        self.assertIn("pv", signals)
        self.assertIn("grid", signals)
        self.assertIn("battery", signals)
        self.assertIn("load", signals)
        self.assertEqual(signals["pv"]["production"], 0)
        self.assertEqual(signals["grid"]["import"], 0)
        self.assertEqual(signals["grid"]["export"], 0)
