"""
Automated unit test suite for CLI Calculator App.
Tests SafeEvaluator, UnitConverter, StatsCalculator, and CLI command parsers.
"""

import math
import unittest
from calculator import CalculationError, SafeEvaluator, StatsCalculator, UnitConverter
from cli import process_convert_command, process_stats_command


class TestSafeEvaluator(unittest.TestCase):
    """Tests core math evaluator and expression parsing."""

    def setUp(self):
        self.evaluator = SafeEvaluator()

    def test_basic_arithmetic(self):
        self.assertEqual(self.evaluator.evaluate("2 + 3"), 5)
        self.assertEqual(self.evaluator.evaluate("10 - 4"), 6)
        self.assertEqual(self.evaluator.evaluate("3 * 4"), 12)
        self.assertEqual(self.evaluator.evaluate("15 / 3"), 5)
        self.assertEqual(self.evaluator.evaluate("17 // 5"), 3)
        self.assertEqual(self.evaluator.evaluate("17 % 5"), 2)
        self.assertEqual(self.evaluator.evaluate("2 ^ 3"), 8)
        self.assertEqual(self.evaluator.evaluate("2 ** 4"), 16)

    def test_operator_precedence(self):
        self.assertEqual(self.evaluator.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.evaluator.evaluate("(2 + 3) * 4"), 20)
        self.assertEqual(self.evaluator.evaluate("10 - 2 * 3 + 4 / 2"), 6)

    def test_scientific_functions(self):
        self.assertAlmostEqual(self.evaluator.evaluate("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(self.evaluator.evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(self.evaluator.evaluate("sqrt(16)"), 4)
        self.assertAlmostEqual(self.evaluator.evaluate("log10(100)"), 2.0)
        self.assertAlmostEqual(self.evaluator.evaluate("ln(e)"), 1.0)
        self.assertEqual(self.evaluator.evaluate("abs(-42)"), 42)
        self.assertEqual(self.evaluator.evaluate("floor(3.9)"), 3)
        self.assertEqual(self.evaluator.evaluate("ceil(3.1)"), 4)
        self.assertEqual(self.evaluator.evaluate("gcd(12, 18)"), 6)
        self.assertEqual(self.evaluator.evaluate("lcm(4, 6)"), 12)
        self.assertEqual(self.evaluator.evaluate("round(3.14159, 2)"), 3.14)

    def test_constants(self):
        self.assertAlmostEqual(self.evaluator.evaluate("pi"), math.pi)
        self.assertAlmostEqual(self.evaluator.evaluate("e"), math.e)
        self.assertAlmostEqual(self.evaluator.evaluate("tau"), math.tau)
        self.assertAlmostEqual(self.evaluator.evaluate("phi"), 1.618033988749895)
        self.assertEqual(self.evaluator.evaluate("c"), 299792458)

    def test_factorial(self):
        self.assertEqual(self.evaluator.evaluate("5!"), 120)
        self.assertEqual(self.evaluator.evaluate("(2 + 3)!"), 120)
        self.assertEqual(self.evaluator.evaluate("factorial(6)"), 720)

    def test_variables(self):
        self.assertEqual(self.evaluator.evaluate("x = 10"), 10)
        self.assertEqual(self.evaluator.evaluate("y = 5"), 5)
        self.assertEqual(self.evaluator.evaluate("x * y"), 50)
        self.assertEqual(self.evaluator.evaluate("ans"), 50)
        self.assertEqual(self.evaluator.evaluate("r = 5"), 5)
        self.assertAlmostEqual(self.evaluator.evaluate("area = pi * r^2"), math.pi * 25)

    def test_errors(self):
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("10 / 0")
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("2 + * 3")
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("undefined_var + 5")
        with self.assertRaises(CalculationError):
            self.evaluator.evaluate("pi = 10")  # Attempt to overwrite constant


class TestUnitConverter(unittest.TestCase):
    """Tests unit conversions."""

    def test_distance(self):
        res = UnitConverter.convert(1, "km", "m")
        self.assertEqual(res['result'], 1000)

        res = UnitConverter.convert(1, "mile", "feet")
        self.assertAlmostEqual(res['result'], 5280, places=1)

    def test_mass(self):
        res = UnitConverter.convert(1, "kg", "g")
        self.assertEqual(res['result'], 1000)

        res = UnitConverter.convert(1, "lb", "oz")
        self.assertEqual(res['result'], 16)

    def test_temperature(self):
        res = UnitConverter.convert(0, "C", "F")
        self.assertEqual(res['result'], 32)

        res = UnitConverter.convert(100, "C", "F")
        self.assertEqual(res['result'], 212)

        res = UnitConverter.convert(0, "C", "K")
        self.assertAlmostEqual(res['result'], 273.15)

    def test_time_and_data(self):
        res = UnitConverter.convert(2, "hours", "minutes")
        self.assertEqual(res['result'], 120)

        res = UnitConverter.convert(1, "GB", "MB")
        self.assertEqual(res['result'], 1024)

    def test_invalid_conversion(self):
        with self.assertRaises(CalculationError):
            UnitConverter.convert(10, "kg", "miles")


class TestStatsCalculator(unittest.TestCase):
    """Tests statistical calculations."""

    def test_summary_stats(self):
        data = [10, 20, 30, 40, 50]
        stats = StatsCalculator.calculate(data)
        self.assertEqual(stats['count'], 5)
        self.assertEqual(stats['sum'], 150)
        self.assertEqual(stats['min'], 10)
        self.assertEqual(stats['max'], 50)
        self.assertEqual(stats['mean'], 30)
        self.assertEqual(stats['median'], 30)

    def test_empty_dataset(self):
        with self.assertRaises(CalculationError):
            StatsCalculator.calculate([])


class TestCLIParsers(unittest.TestCase):
    """Tests CLI command syntax processing."""

    def test_convert_command(self):
        res = process_convert_command("convert 10 km to miles")
        self.assertEqual(res['value'], 10)
        self.assertEqual(res['from_unit'], "km")
        self.assertEqual(res['to_unit'], "miles")

    def test_stats_command(self):
        res = process_stats_command("stats 10, 20, 30, 40, 50")
        self.assertEqual(res['count'], 5)
        self.assertEqual(res['mean'], 30)


if __name__ == '__main__':
    unittest.main()
