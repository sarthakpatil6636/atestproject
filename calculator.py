"""
Core evaluation engine for CLI Calculator App.
Includes AST-based safe math parser, unit converter, and statistics calculator.
"""

import ast
import math
import re
import statistics
from typing import Any, Dict, List, Union


class CalculationError(Exception):
    """Custom exception for calculation errors."""
    pass


class SafeEvaluator:
    """
    Safely evaluates mathematical expressions using Python's AST module.
    Prevents unsafe arbitrary code execution while supporting rich math functionality.
    """

    ALLOWED_FUNCTIONS = {
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'sinh': math.sinh,
        'cosh': math.cosh,
        'tanh': math.tanh,
        'sqrt': math.sqrt,
        'cbrt': getattr(math, 'cbrt', lambda x: x ** (1/3)),
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'log2': math.log2,
        'ln': math.log,
        'abs': abs,
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'radians': math.radians,
        'degrees': math.degrees,
        'factorial': math.factorial,
        'gcd': math.gcd,
        'lcm': getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b)),
        'min': min,
        'max': max,
        'sum': sum,
    }

    ALLOWED_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
        'inf': math.inf,
        'phi': (1 + math.sqrt(5)) / 2,  # Golden Ratio
        'c': 299792458,                 # Speed of light in m/s
        'g': 9.80665,                   # Standard gravity in m/s^2
    }

    def __init__(self):
        self.variables: Dict[str, Union[int, float]] = dict(self.ALLOWED_CONSTANTS)
        self.variables['ans'] = 0.0
        self.history: List[Dict[str, Any]] = []

    def evaluate(self, expr_str: str) -> Union[int, float]:
        """
        Evaluates a mathematical expression string or variable assignment.
        Returns the numerical result.
        """
        expr_str = expr_str.strip()
        if not expr_str:
            raise CalculationError("Empty expression")

        # Handle variable assignment (e.g. x = 5 + 3 or r = sin(pi/4))
        if '=' in expr_str and not expr_str.startswith(('==', '!=', '<=', '>=')):
            parts = expr_str.split('=', 1)
            var_name = parts[0].strip()
            rhs_str = parts[1].strip()

            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', var_name):
                raise CalculationError(f"Invalid variable name '{var_name}'")
            if var_name in self.ALLOWED_CONSTANTS:
                raise CalculationError(f"Cannot overwrite built-in constant '{var_name}'")

            result = self.evaluate(rhs_str)
            self.variables[var_name] = result
            self.variables['ans'] = result
            self.history.append({'expr': expr_str, 'result': result})
            return result

        # Preprocess expression (e.g. replace ^ with ** if needed, N! with factorial(N))
        processed_expr = self._preprocess(expr_str)

        try:
            tree = ast.parse(processed_expr, mode='eval')
        except SyntaxError as err:
            raise CalculationError(f"Invalid syntax: {err.msg}") from err

        result = self._eval_node(tree.body)

        # Normalize floats if whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        self.variables['ans'] = result
        self.history.append({'expr': expr_str, 'result': result})
        return result

    def _preprocess(self, expr: str) -> str:
        """Preprocesses math expressions for user convenience."""
        # Replace caret ^ with ** for standard high-precedence exponentiation
        expr = expr.replace('^', '**')
        # Postfix factorial: e.g. 5! -> factorial(5), (2+3)! -> factorial(2+3)
        # Regex replacement for numbers/identifiers followed by !
        expr = re.sub(r'(\d+|\b[a-zA-Z_][a-zA-Z0-9_]*\b|\([^\(\)]+\))!', r'factorial(\1)', expr)
        return expr

    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """Recursively evaluates AST nodes safely."""

        if isinstance(node, ast.Constant):  # Numbers (int, float)
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculationError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.Name):  # Variables / Constants
            var_name = node.id
            if var_name in self.variables:
                return self.variables[var_name]
            elif var_name in self.ALLOWED_FUNCTIONS:
                raise CalculationError(f"'{var_name}' is a function, not a variable")
            raise CalculationError(f"Undefined variable or constant: '{var_name}'")

        elif isinstance(node, ast.UnaryOp):  # Unary + or -
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise CalculationError(f"Unsupported unary operator: {type(node.op).__name__}")

        elif isinstance(node, ast.BinOp):  # Binary operations (+, -, *, /, //, %, **, ^)
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = node.op

            if isinstance(op, ast.Add):
                return left + right
            elif isinstance(op, ast.Sub):
                return left - right
            elif isinstance(op, ast.Mult):
                return left * right
            elif isinstance(op, ast.Div):
                if right == 0:
                    raise CalculationError("Division by zero")
                return left / right
            elif isinstance(op, ast.FloorDiv):
                if right == 0:
                    raise CalculationError("Division by zero")
                return left // right
            elif isinstance(op, ast.Mod):
                if right == 0:
                    raise CalculationError("Modulo by zero")
                return left % right
            elif isinstance(op, (ast.Pow, ast.BitXor)):  # Support both ** and ^ for power
                try:
                    return left ** right
                except OverflowError:
                    raise CalculationError("Result too large (overflow)")
            raise CalculationError(f"Unsupported binary operator: {type(op).__name__}")

        elif isinstance(node, ast.Call):  # Function calls (e.g. sin(x), log(100, 10))
            if not isinstance(node.func, ast.Name):
                raise CalculationError("Function call must be a named function")

            func_name = node.func.id
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise CalculationError(f"Unknown or disallowed function: '{func_name}'")

            func = self.ALLOWED_FUNCTIONS[func_name]
            args = [self._eval_node(arg) for arg in node.args]

            try:
                result = func(*args)
                if isinstance(result, complex):
                    raise CalculationError("Complex number results are not supported")
                return result
            except TypeError as err:
                raise CalculationError(f"Invalid arguments for {func_name}(): {err}") from err
            except ValueError as err:
                raise CalculationError(f"Math domain error in {func_name}(): {err}") from err
            except OverflowError:
                raise CalculationError(f"Overflow error in {func_name}()")

        raise CalculationError(f"Unsupported expression syntax: {type(node).__name__}")


class UnitConverter:
    """Converts between common physical units."""

    DISTANCE_BASE = 'm'
    DISTANCE = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1.0,
        'km': 1000.0,
        'inch': 0.0254,
        'inches': 0.0254,
        'in': 0.0254,
        'ft': 0.3048,
        'feet': 0.3048,
        'foot': 0.3048,
        'yd': 0.9144,
        'yard': 0.9144,
        'yards': 0.9144,
        'mi': 1609.344,
        'mile': 1609.344,
        'miles': 1609.344,
    }

    MASS_BASE = 'kg'
    MASS = {
        'mg': 0.000001,
        'g': 0.001,
        'kg': 1.0,
        'oz': 0.028349523125,
        'ounce': 0.028349523125,
        'ounces': 0.028349523125,
        'lb': 0.45359237,
        'lbs': 0.45359237,
        'pound': 0.45359237,
        'pounds': 0.45359237,
    }

    TIME_BASE = 'sec'
    TIME = {
        'ms': 0.001,
        's': 1.0,
        'sec': 1.0,
        'second': 1.0,
        'seconds': 1.0,
        'min': 60.0,
        'minute': 60.0,
        'minutes': 60.0,
        'h': 3600.0,
        'hr': 3600.0,
        'hour': 3600.0,
        'hours': 3600.0,
        'day': 86400.0,
        'days': 86400.0,
        'week': 604800.0,
        'weeks': 604800.0,
        'yr': 31536000.0,
        'year': 31536000.0,
        'years': 31536000.0,
    }

    DATA_BASE = 'bytes'
    DATA = {
        'b': 1.0,
        'byte': 1.0,
        'bytes': 1.0,
        'kb': 1024.0,
        'mb': 1024.0 ** 2,
        'gb': 1024.0 ** 3,
        'tb': 1024.0 ** 4,
    }

    TEMP_UNITS = {'c', 'celsius', 'f', 'fahrenheit', 'k', 'kelvin'}

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Converts value from unit to target unit."""
        u_from = from_unit.lower().strip()
        u_to = to_unit.lower().strip()

        # Temperature handling
        if u_from in cls.TEMP_UNITS and u_to in cls.TEMP_UNITS:
            return cls._convert_temperature(value, u_from, u_to)

        # Standard linear categories
        for category, units in [('Distance', cls.DISTANCE), ('Mass', cls.MASS), ('Time', cls.TIME), ('Data', cls.DATA)]:
            if u_from in units and u_to in units:
                base_value = value * units[u_from]
                converted_value = base_value / units[u_to]
                if isinstance(converted_value, float) and converted_value.is_integer():
                    converted_value = int(converted_value)
                return {
                    'category': category,
                    'value': value,
                    'from_unit': from_unit,
                    'result': converted_value,
                    'to_unit': to_unit
                }

        raise CalculationError(f"Cannot convert between '{from_unit}' and '{to_unit}'")

    @classmethod
    def _convert_temperature(cls, val: float, u_from: str, u_to: str) -> Dict[str, Any]:
        if u_from in ('c', 'celsius'):
            c_val = val
        elif u_from in ('f', 'fahrenheit'):
            c_val = (val - 32) * 5 / 9
        elif u_from in ('k', 'kelvin'):
            c_val = val - 273.15
        else:
            raise CalculationError(f"Unknown temperature unit '{u_from}'")

        if u_to in ('c', 'celsius'):
            res = c_val
        elif u_to in ('f', 'fahrenheit'):
            res = (c_val * 9 / 5) + 32
        elif u_to in ('k', 'kelvin'):
            res = c_val + 273.15
        else:
            raise CalculationError(f"Unknown temperature unit '{u_to}'")

        if isinstance(res, float) and res.is_integer():
            res = int(res)

        return {
            'category': 'Temperature',
            'value': val,
            'from_unit': u_from.capitalize(),
            'result': res,
            'to_unit': u_to.capitalize()
        }


class StatsCalculator:
    """Computes summary statistics for a dataset."""

    @staticmethod
    def calculate(data: List[float]) -> Dict[str, Any]:
        if not data:
            raise CalculationError("Cannot compute statistics on empty data set")

        n = len(data)
        total = sum(data)
        mean_val = statistics.mean(data)
        median_val = statistics.median(data)

        try:
            mode_val = statistics.mode(data)
        except statistics.StatisticsError:
            mode_val = "N/A (no unique mode)"

        variance_val = statistics.variance(data) if n > 1 else 0.0
        stdev_val = statistics.stdev(data) if n > 1 else 0.0

        return {
            'count': n,
            'sum': total,
            'min': min(data),
            'max': max(data),
            'mean': mean_val,
            'median': median_val,
            'mode': mode_val,
            'variance': variance_val,
            'stdev': stdev_val
        }
