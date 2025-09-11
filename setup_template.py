"""setup."""
"""Setup template file."""
import os
from setuptools import setup, find_packages

# Read README
with open(os.path.join(os.path.dirname(__file__), 'README.md'),
          encoding='utf-8') as f:
    README = f.read()

setup(
    name='pumpwood-djangoauth',
    version='{VERSION}',
    include_package_data=True,
    license='BSD-3-Clause License',
    description='Assist creating views for Django using Pumpwood pattern.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/Murabei-OpenSource-Codes/pumpwood-djangoauth',
    author='Murabei Data Science',
    author_email='a.baceti@murabei.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    package_data={"": ['*.html', '*.sql']},
    install_requires={
        "Django>=4.0.0",
        "djangorestframework>=3.13",
        "python-slugify>=8.0.1",
        "pandas>=1.3.1",
        "django-flat-json-widget>=0.1.3",
        "PyJWT>=2.7.0",
        "django-rest-knox==4.2.0",
        "pumpwood-communication>=1.0",
        "pumpwood-kong",
        "twilio==8.11.0",
        "lazy-string==1.0.0"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
)
