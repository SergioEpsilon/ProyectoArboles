"""Unit tests for FlightFactory metadata handling."""

import unittest

from services.flight_factory import FlightFactory


class TestFlightFactory(unittest.TestCase):
    def test_build_preserves_explicit_zero_values(self):
        data = {
            "codigo": "SB100",
            "precioBase": 0,
            "precioFinal": 0,
            "pasajeros": 0,
            "prioridad": 3,
            "promocion": False,
            "alerta": True,
        }

        metadata = FlightFactory.build(data, "SB100")

        self.assertEqual(metadata["precioBase"], 0)
        self.assertEqual(metadata["precioFinal"], 0)
        self.assertEqual(metadata["pasajeros"], 0)
        self.assertFalse(metadata["promocion"])
        self.assertTrue(metadata["alerta"])

    def test_build_defaults_final_price_only_when_missing(self):
        metadata = FlightFactory.build({"precioBase": 150}, "SB200")

        self.assertEqual(metadata["precioBase"], 150)
        self.assertEqual(metadata["precioFinal"], 150)

    def test_merge_preserves_explicit_zero_price_update(self):
        merged = FlightFactory.merge(
            {"precioBase": 120, "precioFinal": 140, "codigo": "SB300"},
            {"precioBase": 0},
        )

        self.assertEqual(merged["precioBase"], 0)
        self.assertEqual(merged["precioFinal"], 0)
        self.assertEqual(merged["codigo"], "SB300")


if __name__ == "__main__":
    unittest.main()
