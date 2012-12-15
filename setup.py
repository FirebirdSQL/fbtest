#!/usr/bin/env python
"""fbtest is set of tools for Firebird RDBMS QA.

"""
from setuptools import setup, find_packages
from fbtest import __version__

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database',
]

setup(name='fbtest', 
        version=__version__,
        description = 'Firebird QA tools.', 
        url='http://www.firebirdsql.org/en/quality-assurance-status/',
        classifiers=classifiers,
        keywords=['Firebird'],
        license='IDPL',
        author='Pavel Cisar',
        author_email='pcisar@users.sourceforge.net',
        long_description=__doc__,
    install_requires=[],
    setup_requires=[],
    packages=find_packages(exclude=['ez_setup']),
    test_suite='nose.collector',
    #include_package_data=True,
    package_data={'': ['*.txt'],
                  },
    #message_extractors={'fdb': [
            #('**.py', 'python', None),
            #('public/**', 'ignore', None)]},
    zip_safe=False,
    entry_points="""
    """,
)
