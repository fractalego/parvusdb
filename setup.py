from setuptools import setup

setup(name='parvusdb',
      version='0.0.6',
      description='A lightweight in-memory graph database',
      url='http://github.com/fractalego/parvusdb',
      author='Alberto Cetoli',
      author_email='alberto@nlulite.com',
      license='MIT',
      packages=['parvusdb', 'parvusdb.utils'],
      install_requires=[
          'python-igraph',
          'hy',
      ],
      zip_safe=False)
