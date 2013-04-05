#!/usr/bin/env python
"""fbtest is set of tools for Firebird RDBMS QA.

"""
from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Database',
    'Topic :: Software Development',
    'Intended Audience :: Developers ',
]

setup(name='fbtest', 
      version='1.0',
      description = 'Firebird QA tools.', 
      url='http://www.firebirdsql.org/en/quality-assurance-status/',
      classifiers=classifiers,
      keywords=['Firebird','QA'],
      license='IDPL',
      author='Pavel Cisar',
      author_email='pcisar@users.sourceforge.net',
      long_description=__doc__,
      install_requires=['distribute','fdb>=0.9.9','mako>=0.7.0','rpyc>=3.2'],
      setup_requires=[],
      packages=find_packages(exclude=['ez_setup']),
      test_suite='nose.collector',
      include_package_data=True,
      package_data={'': ['*.txt','*.rst'],
                    },
      use_2to3 = True,
      #message_extractors={'fbtest': [
                                  #('**.py', 'python', None),
                                  #('public/**', 'ignore', None)]},
      zip_safe=True,
      entry_points={'console_scripts': [
            'fbt_run = fbtest:run_tests',
            'fbt_server = fbtest:run_server',
            'fbt_analyze = fbtest:run_analyze',
            'fbt_update = fbtest:run_update',
            'fbt_view = fbtest:run_view',
            'fbt_archive = fbtest:run_archive',
        ],
    },
)
