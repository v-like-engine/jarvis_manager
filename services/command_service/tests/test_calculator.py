"""Tests for calculator module."""

import unittest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.calculator import Calculator


class TestCalculator(unittest.TestCase):
    """Test calculator."""

    def setUp(self):
        """Set up test fixtures."""
        self.calc = Calculator()

    def test_basic_addition(self):
        """Test basic addition."""
        result = self.calc.calculate('2 + 2')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 4)

    def test_basic_subtraction(self):
        """Test basic subtraction."""
        result = self.calc.calculate('10 - 3')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 7)

    def test_basic_multiplication(self):
        """Test basic multiplication."""
        result = self.calc.calculate('5 * 4')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 20)

    def test_basic_division(self):
        """Test basic division."""
        result = self.calc.calculate('15 / 3')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 5)

    def test_division_by_zero(self):
        """Test division by zero."""
        result = self.calc.calculate('10 / 0')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_complex_expression(self):
        """Test complex expression."""
        result = self.calc.calculate('(2 + 3) * 4')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 20)

    def test_power(self):
        """Test power operation."""
        result = self.calc.calculate('2 ** 3')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 8)

    def test_natural_language_addition(self):
        """Test natural language addition."""
        result = self.calc.calculate('5 plus 3')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 8)

    def test_natural_language_multiplication(self):
        """Test natural language multiplication."""
        result = self.calc.calculate('6 times 7')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 42)

    def test_square_root(self):
        """Test square root."""
        result = self.calc.calculate('sqrt(16)')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 4)

    def test_negative_numbers(self):
        """Test negative numbers."""
        result = self.calc.calculate('-5 + 3')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], -2)

    def test_decimal_numbers(self):
        """Test decimal numbers."""
        result = self.calc.calculate('2.5 * 4')

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 10)

    def test_unsafe_expression(self):
        """Test unsafe expression is rejected."""
        result = self.calc.calculate('import os')

        self.assertFalse(result['success'])
        self.assertIn('error', result)

    def test_add_method(self):
        """Test add method."""
        result = self.calc.add(5, 3)

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 8)

    def test_subtract_method(self):
        """Test subtract method."""
        result = self.calc.subtract(10, 4)

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 6)

    def test_multiply_method(self):
        """Test multiply method."""
        result = self.calc.multiply(7, 6)

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 42)

    def test_divide_method(self):
        """Test divide method."""
        result = self.calc.divide(20, 5)

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 4)

    def test_percentage(self):
        """Test percentage calculation."""
        result = self.calc.percentage(200, 10)  # 10% of 200

        self.assertTrue(result['success'])
        self.assertEqual(result['result'], 20)


if __name__ == '__main__':
    unittest.main()
