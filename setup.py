"""setup."""
"""Setup template file."""
import os
import re
from setuptools import setup, find_packages


def parse_requirements(filename):
    """Load requirements from a requirements.txt file."""
    with open(filename) as f:
        lines = f.read().splitlines()

    requirements = []
    for line in lines:
        # Skip comments and empty lines
        if line.startswith('#') or not line.strip():
            continue

        # Remove whitespace and any trailing comments
        line = re.sub(r'\s*#.*$', '', line).strip()
        if line:  # Add if not empty after cleanup
            requirements.append(line)

    return requirements


# Read README
with open(os.path.join(os.path.dirname(__file__), 'README.md'),
          encoding='utf-8') as f:
    README = f.read()

# Parse requirements.txt
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
requirements = parse_requirements(requirements_path)


setup(
    name='pumpwood-djangoauth',
    version='2.0.3',
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
    package_data={"": ['*.html']},
    install_requires=requirements,  # Uses parsed requirements.txt
    packages=find_packages(where="src"),
    python_requires=">=3.6",
)
