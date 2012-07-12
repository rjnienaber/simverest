import sys

extra = {}
if sys.version_info >= (3, 0):
    extra.update(use_2to3=True)

from setuptools import setup, find_packages, Command

setup(name='simverest',
      version='0.5.0',
      description='A simple dashboard for the Varnish Cache',
      long_description=open('README.rst').read(),
      data_files=[('', ['README.rst'])],
      classifiers=[
            'License :: OSI Approved :: BSD License',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
          ],
      keywords='varnish',
      author='Richard Nienaber',
      url='https://github.com/rjnienaber/simverest',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      platforms=["any"],
      tests_require=['mock', 'argparse'],
      **extra
)
