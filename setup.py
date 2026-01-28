from setuptools import setup, find_packages

setup(
    name="refactoring-swarm",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "python-dotenv",
        "pytest",
    ],
)
