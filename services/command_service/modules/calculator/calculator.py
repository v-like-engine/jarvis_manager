"""Calculator for mathematical operations."""

import logging
import re
import math
from typing import Dict, Any, Union

logger = logging.getLogger(__name__)


class Calculator:
    """
    Perform mathematical calculations.

    Supports:
    - Basic operations: +, -, *, /
    - Advanced: power, square root, percentages
    - Safe evaluation with limited scope
    """

    # Allowed mathematical functions
    SAFE_FUNCTIONS = {
        'sqrt': math.sqrt,
        'pow': math.pow,
        'abs': abs,
        'round': round,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'floor': math.floor,
        'ceil': math.ceil,
    }

    # Allowed constants
    SAFE_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
    }

    def __init__(self):
        """Initialize calculator."""
        logger.info("Calculator initialized")

    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Calculate a mathematical expression.

        Args:
            expression: Mathematical expression as string

        Returns:
            Dictionary with calculation result
        """
        try:
            # Clean and normalize expression
            expression = self._normalize_expression(expression)

            # Safety check
            if not self._is_safe_expression(expression):
                return {
                    'success': False,
                    'error': 'Expression contains unsafe operations'
                }

            # Evaluate expression
            result = self._safe_eval(expression)

            # Format result
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)  # Limit decimal places

            return {
                'success': True,
                'expression': expression,
                'result': result,
                'message': f"{expression} = {result}"
            }

        except ZeroDivisionError:
            logger.error("Division by zero")
            return {
                'success': False,
                'error': 'Cannot divide by zero'
            }
        except ValueError as e:
            logger.error(f"Invalid value: {e}")
            return {
                'success': False,
                'error': f'Invalid value: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {
                'success': False,
                'error': f'Calculation error: {str(e)}'
            }

    def _normalize_expression(self, expr: str) -> str:
        """
        Normalize mathematical expression.

        Args:
            expr: Raw expression

        Returns:
            Normalized expression
        """
        # Convert to lowercase
        expr = expr.lower()

        # Replace common words with operators
        replacements = {
            ' plus ': '+',
            ' add ': '+',
            ' minus ': '-',
            ' subtract ': '-',
            ' times ': '*',
            ' multiplied by ': '*',
            ' multiply ': '*',
            ' divided by ': '/',
            ' divide ': '/',
            ' to the power of ': '**',
            ' squared': '**2',
            ' cubed': '**3',
            'percent': '/100',
            '%': '/100',
        }

        for old, new in replacements.items():
            expr = expr.replace(old, new)

        # Remove extra spaces
        expr = ' '.join(expr.split())

        return expr

    def _is_safe_expression(self, expr: str) -> bool:
        """
        Check if expression is safe to evaluate.

        Args:
            expr: Expression to check

        Returns:
            True if safe, False otherwise
        """
        # Forbidden keywords/patterns
        forbidden = [
            '__', 'import', 'exec', 'eval', 'compile', 'open', 'file',
            'input', 'raw_input', 'reload', 'globals', 'locals', 'vars',
            'dir', 'lambda', 'class', 'def', 'yield', 'del'
        ]

        expr_lower = expr.lower()

        for keyword in forbidden:
            if keyword in expr_lower:
                logger.warning(f"Forbidden keyword in expression: {keyword}")
                return False

        return True

    def _safe_eval(self, expr: str) -> Union[int, float]:
        """
        Safely evaluate mathematical expression.

        Args:
            expr: Expression to evaluate

        Returns:
            Result of evaluation
        """
        # Create safe namespace
        safe_dict = {
            '__builtins__': {},
            **self.SAFE_FUNCTIONS,
            **self.SAFE_CONSTANTS
        }

        # Evaluate
        result = eval(expr, safe_dict, {})

        return result

    def add(self, a: float, b: float) -> Dict[str, Any]:
        """Add two numbers."""
        return self.calculate(f"{a} + {b}")

    def subtract(self, a: float, b: float) -> Dict[str, Any]:
        """Subtract b from a."""
        return self.calculate(f"{a} - {b}")

    def multiply(self, a: float, b: float) -> Dict[str, Any]:
        """Multiply two numbers."""
        return self.calculate(f"{a} * {b}")

    def divide(self, a: float, b: float) -> Dict[str, Any]:
        """Divide a by b."""
        return self.calculate(f"{a} / {b}")

    def power(self, base: float, exponent: float) -> Dict[str, Any]:
        """Raise base to exponent."""
        return self.calculate(f"{base} ** {exponent}")

    def square_root(self, n: float) -> Dict[str, Any]:
        """Calculate square root."""
        return self.calculate(f"sqrt({n})")

    def percentage(self, value: float, percent: float) -> Dict[str, Any]:
        """Calculate percentage of a value."""
        return self.calculate(f"{value} * {percent} / 100")
