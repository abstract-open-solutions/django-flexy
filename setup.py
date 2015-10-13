from setuptools import setup, find_packages
import os


version = '0.1.dev0'


def read(*path):
    with open(os.path.join(os.path.dirname(__file__), *path)) as data:
        return data.read()


setup(
    name='django-flexy',
    version=version,
    description="Django elasticsearch utilities",
    long_description=(
        read("README.rst") + "\n" +
        read("docs", "HISTORY.rst")
    ),
    classifiers=[
        "Programming Language :: Python",
        "Private :: Do Not Upload"
    ],
    keywords='',
    author='Simone Deponti',
    author_email='simone.deponti@abstract.it',
    url='http://git.abstract.it/suono.it/django-flexy/',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'mock',
        'Django',
        'elasticsearch-dsl',
        'django-appconf'
    ]
)
