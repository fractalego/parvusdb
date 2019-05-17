from setuptools import setup
from distutils.extension import Extension

packages = ['parvusdb', 'parvusdb.utils']
extensions = [Extension('parvusdb', ['parvusdb' + '/__init__.py']),
              Extension('parvusdb.utils', ['parvusdb/utils/__init__.py',
                                           'parvusdb/utils/aux.py',
                                           'parvusdb/utils/code_container.py',
                                           'parvusdb/utils/cache.py'
                                           'parvusdb/utils/graph_builder.py',
                                           'parvusdb/utils/graph_database.py',
                                           'parvusdb/utils/node_matcher.py'
                                           ])]

setup(name='parvusdb',
      version='0.0.25',
      description='A lightweight in-memory graph database',
      url='http://github.com/fractalego/parvusdb',
      author='Alberto Cetoli',
      author_email='alberto@nlulite.com',
      license='MIT',
      packages=packages,
      install_requires=[
          'python-igraph==0.7.1.post6',
          'hy==0.13.0',
      ],
      zip_safe=False)
