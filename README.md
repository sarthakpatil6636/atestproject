# CLI Calculator App

A feature-rich, interactive Command-Line Interface (CLI) Calculator app built with Python, [`rich`](https://github.com/Textualize/rich), and [`prompt_toolkit`](https://github.com/prompt-toolkit/python-prompt-toolkit).

Features safe AST-based mathematical evaluation, variable memory, physical unit conversions, summary statistics computation, interactive REPL shell with tab completion & syntax highlighting, and script piping support.

---

## Features

- **Safe Math Evaluator**: AST parser prevents arbitrary code injection while supporting arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, `^`, `!`), parenthesized expressions, and trigonometric / scientific functions.
- **Scientific Functions**: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `sqrt`, `cbrt`, `exp`, `log`, `log10`, `log2`, `ln`, `abs`, `round`, `floor`, `ceil`, `radians`, `degrees`, `factorial`, `gcd`, `lcm`.
- **Built-in Constants**: `pi`, `e`, `tau`, `phi` (golden ratio), `c` (speed of light), `g` (gravity).
- **Variable Assignments & Memory**: Define custom variables (`x = 10`, `r = 5`, `area = pi * r^2`) and access the `ans` automatic variable.
- **Interactive REPL Shell**: Includes tab completion, command history (`~/.cli_calc_history`), and styled prompt.
- **Unit Conversion**: Distance, Mass, Temperature, Data, and Time units (e.g. `convert 10 km to miles`).
- **Summary Statistics**: Compute count, sum, mean, median, mode, variance, std dev, min, and max for datasets.
- **Direct CLI Execution & Script Piping**: Pass expressions as terminal arguments, with `--raw` flag for pure text output.

---

## Quick Start

### 1. Interactive REPL Mode
Run the calculator without arguments to launch the interactive shell:

```bash
python3 calc.py
```

### 2. Direct Expression Evaluation
Evaluate math expressions directly from the terminal:

```bash
python3 calc.py "2 + 3 * sin(pi / 4)"
```

Use `-r` / `--raw` to output unformatted values (ideal for shell scripts and piping):

```bash
python3 calc.py -r "sqrt(256)"
```

### 3. Unit Conversion
Convert between common physical units:

```bash
python3 calc.py "convert 10 km to miles"
python3 calc.py "convert 100 C to F"
python3 calc.py "convert 16 GB to MB"
```

### 4. Summary Statistics
Calculate dataset metrics:

```bash
python3 calc.py "stats 10, 20, 30, 40, 50"
```

---

## Installation (Optional)

Install locally in editable mode so the `calc` command is available anywhere in your terminal:

```bash
pip install -e .
```

After installation, simply run:
```bash
calc
```

---

## Running Unit Tests

Run the test suite with Python's built-in unittest framework:

```bash
python3 -m unittest test_calculator.py
```

---

## Project Structure

- [`calc.py`](file:///Users/anuragpatil/atestproject/calc.py): Main executable entry script.
- [`cli.py`](file:///Users/anuragpatil/atestproject/cli.py): CLI interface, REPL shell, argument parser, and Rich visual styling.
- [`calculator.py`](file:///Users/anuragpatil/atestproject/calculator.py): Core SafeEvaluator (AST parser), UnitConverter, and StatsCalculator classes.
- [`test_calculator.py`](file:///Users/anuragpatil/atestproject/test_calculator.py): Automated test suite.
- [`setup.py`](file:///Users/anuragpatil/atestproject/setup.py): Package setup & entry point configuration.
