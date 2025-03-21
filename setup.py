from os.path import dirname, join
from setuptools import setup, find_packages


with open(join(dirname(__file__), 'api_test_ez/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()


install_requires = [
    'tablib==3.2.1',
    'ddt~=1.5.0',
    'urllib3~=1.26.20',
    'requests~=2.30.0',
    'pytest~=7.1.2',
    'openpyxl==3.0.10',
    'BeautifulReport~=0.1.3',
    'marshmallow~=3.16.0',
    'unittestreport~=1.5.6'
]


setup(
    name='ApiTestEz',
    version=version,
    url='https://github.com/bruce4520196/ApiTestEz',
    description='An easier api test framework.',
    author='Bruce Cai',
    maintainer='Bruce Cai',
    maintainer_email='whiteghostcat@gmail.com',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.5',
    install_requires=install_requires,
)
