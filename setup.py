from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='redfish_utilities',
      version='0.5.0',
      description='Redfish Utilities',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author = 'DMTF, https://www.dmtf.org/standards/feedback',
      license='BSD 3-clause "New" or "Revised License"',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Topic :: Communications'
      ],
      keywords='Redfish',
      url='https://github.com/DMTF/Redfish-Tacklebox',
      packages=['redfish_utilities'],
      scripts=['scripts/sensor_list'],
      install_requires=[
          'redfish'
      ])
