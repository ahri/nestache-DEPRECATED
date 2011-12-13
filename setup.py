"""
Nestache
--------------

An alternative (and stricted) View for pystache supporting nesting.

Links
`````

* `development version
  <http://github.com/ahri/nestache>`_

"""
from setuptools import setup

setup(
    name='Nestache',
    version='0.2.0',
    url='http://github.com/ahri/nestache',
    license='AGPLv3',
    author='Adam Piper',
    author_email='adam@ahri.net',
    description='Nested View for Mustache',
    long_description=__doc__,
    packages=['nestache'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pystache>=0.3.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
