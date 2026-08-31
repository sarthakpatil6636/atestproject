"""
Command-Line Interface and REPL for CLI Calculator App.
Utilizes Rich for terminal UI styling and Prompt Toolkit for interactive shell features.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style as PtStyle

from calculator import CalculationError, SafeEvaluator, StatsCalculator, UnitConverter

# Rich custom theme
custom_theme = Theme({
    "primary": "bold cyan",
    "secondary": "bold magenta",
    "success": "bold green",
    "error": "bold red",
    "warning": "bold yellow",
    "muted": "dim white",
    "operator": "bright_blue",
    "number": "bright_green",
})

console = Console(theme=custom_theme)

# Prompt Toolkit Style
pt_style = PtStyle.from_dict({
    'prompt': '#00ffff bold',
    'input': '#ffffff',
})


def print_banner():
    """Prints a styled welcome banner."""
    banner_text = Text()
    banner_text.append("CLI Calculator ", style="bold cyan")
    banner_text.append("v1.0.0\n", style="bold magenta")
    banner_text.append("Type expressions like ", style="dim white")
    banner_text.append("2 + 3 * sin(pi/4)", style="bold yellow")
    banner_text.append(", or try ", style="dim white")
    banner_text.append("help", style="bold green")
    banner_text.append(" for commands.", style="dim white")

    console.print(Panel(banner_text, border_style="cyan", padding=(0, 2)))


def print_help():
    """Displays structured help information."""
    table = Table(title="CLI Calculator - Help Guide", border_style="cyan", show_lines=True)
    table.add_column("Category", style="cyan", width=16)
    table.add_column("Usage / Examples", style="white")

    table.add_row(
        "Basic Math",
        "2 + 3 * 4  |  (10 - 2) / 4  |  5 % 2  |  2 ^ 8  |  5!"
    )
    table.add_row(
        "Functions",
        "sin(pi/2)  |  cos(radians(45))  |  sqrt(16)  |  log10(100)  |  ln(e)  |  factorial(6)\n"
        "gcd(12, 18)  |  lcm(4, 6)  |  abs(-42)  |  round(3.14159, 2)  |  min(4, 1, 9)"
    )
    table.add_row(
        "Constants",
        "pi (3.14159...)  |  e (2.71828...)  |  tau  |  phi (1.61803...)  |  c (299792458 m/s)"
    )
    table.add_row(
        "Variables",
        "x = 10\n"
        "area = pi * r^2\n"
        "ans (stores the previous calculated result)"
    )
    table.add_row(
        "Unit Convert",
        "convert 10 km to miles  |  convert 100 C to F  |  convert 5 kg to lbs\n"
        "convert 16 gb to mb     |  convert 2.5 hours to minutes"
    )
    table.add_row(
        "Statistics",
        "stats 10, 20, 30, 40, 50\n"
        "stats 4.5 9.1 12.3 8.8"
    )
    table.add_row(
        "Commands",
        "vars       - List all defined variables\n"
        "history    - Show calculation history\n"
        "clear      - Clear screen & history\n"
        "help       - Show this help guide\n"
        "exit / q   - Exit the application"
    )

    console.print(table)


def print_vars(evaluator: SafeEvaluator):
    """Displays active user variables and constants."""
    table = Table(title="Variables & Constants", border_style="magenta", show_lines=True)
    table.add_column("Name", style="bold cyan", width=12)
    table.add_column("Value", style="bold green")
    table.add_column("Type", style="dim white", width=12)

    for name, val in evaluator.variables.items():
        is_const = name in evaluator.ALLOWED_CONSTANTS
        val_type = "Constant" if is_const else ("Last Ans" if name == "ans" else "User Variable")
        table.add_row(name, str(val), val_type)

    console.print(table)


def print_history(evaluator: SafeEvaluator):
    """Displays calculation history."""
    if not evaluator.history:
        console.print("[muted]History is empty.[/muted]")
        return

    table = Table(title="Calculation History", border_style="green")
    table.add_column("#", style="dim white", width=4)
    table.add_column("Expression", style="cyan")
    table.add_column("Result", style="bold green")

    for i, item in enumerate(evaluator.history, 1):
        table.add_row(str(i), item['expr'], str(item['result']))

    console.print(table)


def print_stats(stats_dict: dict):
    """Displays formatted statistics summary."""
    table = Table(title="Dataset Summary Statistics", border_style="cyan", show_lines=True)
    table.add_column("Metric", style="bold magenta", width=16)
    table.add_column("Value", style="bold green")

    for key, val in stats_dict.items():
        formatted_val = f"{val:.6f}" if isinstance(val, float) else str(val)
        table.add_row(key.capitalize(), formatted_val)

    console.print(table)


def process_convert_command(command_str: str) -> Optional[dict]:
    """
    Parses unit conversion syntax:
    e.g. 'convert 10 km to miles', 'convert 100 c f'
    """
    pattern = r'^convert\s+([\d\.\-]+)\s+([a-zA-Z]+)(?:\s+to)?\s+([a-zA-Z]+)$'
    match = re.match(pattern, command_str.strip(), re.IGNORECASE)
    if not match:
        raise CalculationError("Invalid convert syntax. Use: convert <value> <from_unit> to <to_unit>")

    val = float(match.group(1))
    from_u = match.group(2)
    to_u = match.group(3)
    return UnitConverter.convert(val, from_u, to_u)


def process_stats_command(command_str: str) -> dict:
    """
    Parses stats command syntax:
    e.g. 'stats 10, 20, 30, 40' or 'stats 1 2 3 4'
    """
    raw_args = command_str[5:].strip()
    if not raw_args:
        raise CalculationError("Invalid stats syntax. Use: stats <number1>, <number2>, ...")

    # Split by comma or whitespace
    parts = re.split(r'[\s,]+', raw_args)
    try:
        numbers = [float(p) for p in parts if p]
    except ValueError:
        raise CalculationError("All items in stats must be valid numbers")

    return StatsCalculator.calculate(numbers)


def run_repl():
    """Runs the interactive REPL shell."""
    evaluator = SafeEvaluator()

    # Create history directory if needed
    history_file = Path.home() / ".cli_calc_history"

    # Auto-completer keywords
    completer_words = list(evaluator.ALLOWED_FUNCTIONS.keys()) + \
                      list(evaluator.ALLOWED_CONSTANTS.keys()) + \
                      ['convert', 'stats', 'vars', 'history', 'clear', 'help', 'exit', 'quit', 'ans']
    completer = WordCompleter(completer_words, ignore_case=True)

    session = PromptSession(
        history=FileHistory(str(history_file)),
        completer=completer
    )

    print_banner()

    while True:
        try:
            user_input = session.prompt([('class:prompt', 'calc > ')], style=pt_style).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[muted]Goodbye![/muted]")
            sys.exit(0)

        if not user_input:
            continue

        cmd_lower = user_input.lower()

        # Handle built-in REPL commands
        if cmd_lower in ('exit', 'quit', 'q'):
            console.print("[muted]Goodbye![/muted]")
            break
        elif cmd_lower == 'help':
            print_help()
            continue
        elif cmd_lower == 'vars':
            print_vars(evaluator)
            continue
        elif cmd_lower == 'history':
            print_history(evaluator)
            continue
        elif cmd_lower == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            continue

        # Convert command
        if cmd_lower.startswith('convert '):
            try:
                res = process_convert_command(user_input)
                console.print(
                    Panel(
                        f"[bold yellow]{res['value']} {res['from_unit']}[/bold yellow] = "
                        f"[bold green]{res['result']} {res['to_unit']}[/bold green] "
                        f"[muted]({res['category']})[/muted]",
                        border_style="cyan"
                    )
                )
            except CalculationError as e:
                console.print(f"[error]Error:[/error] {e}")
            continue

        # Stats command
        if cmd_lower.startswith('stats '):
            try:
                res = process_stats_command(user_input)
                print_stats(res)
            except CalculationError as e:
                console.print(f"[error]Error:[/error] {e}")
            continue

        # Math expression evaluation
        try:
            res = evaluator.evaluate(user_input)
            console.print(f"[bold cyan]=> [/bold cyan][bold green]{res}[/bold green]")
        except CalculationError as e:
            console.print(f"[error]Error:[/error] {e}")
        except Exception as e:
            console.print(f"[error]Unexpected error:[/error] {e}")


def execute_direct(expr: str, raw: bool = False):
    """Executes a single expression directly from CLI arguments."""
    evaluator = SafeEvaluator()
    expr_cleaned = expr.strip()
    cmd_lower = expr_cleaned.lower()

    try:
        if cmd_lower.startswith('convert '):
            res = process_convert_command(expr_cleaned)
            if raw:
                print(res['result'])
            else:
                console.print(f"{res['value']} {res['from_unit']} = [bold green]{res['result']} {res['to_unit']}[/bold green]")
            return

        if cmd_lower.startswith('stats '):
            res = process_stats_command(expr_cleaned)
            if raw:
                print(f"mean: {res['mean']}, median: {res['median']}, std: {res['stdev']}")
            else:
                print_stats(res)
            return

        res = evaluator.evaluate(expr_cleaned)
        if raw:
            print(res)
        else:
            console.print(f"[bold cyan]=> [/bold cyan][bold green]{res}[/bold green]")
    except CalculationError as e:
        if raw:
            print(f"ERROR: {e}", file=sys.stderr)
        else:
            console.print(f"[error]Error:[/error] {e}")
        sys.exit(1)


def main():
    """Main CLI entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="CLI Calculator - Interactive math shell, unit converter & statistical analyzer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  calc                         # Launch interactive shell\n"
               "  calc '2 + 3 * sin(pi/4)'    # Evaluate expression directly\n"
               "  calc -r 'sqrt(144)'         # Evaluate with raw output\n"
               "  calc 'convert 10 km to mi'   # Convert units\n"
               "  calc 'stats 10, 20, 30, 40'  # Summary statistics\n"
    )

    parser.add_argument(
        'expression',
        nargs='?',
        type=str,
        help="Math expression, unit conversion, or stats command to evaluate directly"
    )
    parser.add_argument(
        '-r', '--raw',
        action='store_true',
        help="Print raw result without rich formatting (useful for scripts)"
    )

    args = parser.parse_args()

    if args.expression:
        execute_direct(args.expression, raw=args.raw)
    else:
        run_repl()


if __name__ == '__main__':
    main()
