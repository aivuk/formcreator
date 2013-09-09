from setuptools import setup

setup(name='formcreator',
      version='0.1.1',
      description='Create web forms for command line programs or python functions',
      url='http://github.com/aivuk/formcreator',
      author='Edgar Z. Alvarenga',
      author_email='e@vaz.io',
      license='BSD 2-Clause',
      packages=['formcreator', 'formcreator.fields', 'formcreator.blocks', 'formcreator.static', 'formcreator.templates'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'flask>=0.10.1',
          'flask-login>=0.2.7',
          'sqlalchemy>=0.8.2',
          'flask-sqlalchemy>=1.0',
          'wtforms>=1.0.3',
          'markdown>=2.2.1',
          'ordereddict>=1.1',
      ],
      )
