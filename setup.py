from setuptools import setup, find_packages

setup(
    name="dnu_academic_rating",
    description="Academic calculation based on the official strategy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "Django==3.2.4",
        "django-microsoft-auth==2.4.0",
        "pyjwt==1.7.1",
        "pylint==2.8.3",
    ],
)
