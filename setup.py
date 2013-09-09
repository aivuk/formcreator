from setuptools import setup

setup(name='formcreator',
      version='0.1.0',
      description='Create web forms for command line programs or python functions',
      url='http://github.com/aivuk/formcreator',
      author='Edgar Z. Alvarenga',
      author_email='e@vaz.io',
      license='BSD 2-Clause',
      packages=['formcreator', 'formcreator.fields', 'formcreator.blocks', 'formcreator.static', 'formcreator.templates'],
      include_package_data=True,
      zip_safe=False)
