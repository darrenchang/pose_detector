import os

from setuptools import find_packages, setup


def load_requirements():
    requirements_path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(requirements_path, "requirements.txt"), "r") as f:
        return f.read().splitlines()


setup(
    name="pose",
    version="1.0",
    author="Darren",
    author_email="",
    description="",
    packages=find_packages(),
    zip_safe=False,
    install_requires=load_requirements(),
)
