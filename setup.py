from setuptools import setup, find_packages

setup(
    name="cli-calc-app",
    version="1.0.0",
    description="A feature-rich, interactive CLI calculator with unit conversion and statistics.",
    author="Antigravity",
    packages=find_packages(),
    py_modules=["calc", "cli", "calculator"],
    install_requires=[
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "calc=cli:main",
        ],
    },
    python_requires=">=3.8",
)
