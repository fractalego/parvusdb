from setuptools import setup

packages = ['parvusdb', 'parvusdb.utils']

setup(name='parvusdb',
      version='0.0.16',
      description='A lightweight in-memory graph database',
      url='http://github.com/fractalego/parvusdb',
      author='Alberto Cetoli',
      author_email='alberto@nlulite.com',
      license='MIT',
      packages=packages,
      install_requires=[
          'python-igraph',
          'hy'
      ],
      zip_safe=False)
