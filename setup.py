try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import chasha

setup(name='chasha',
      version=chasha.__version__,
      description='Light-weight Gopher library modeled after Bottle',
      author='Stefan Edwards <saedwards.ecc@gmail.com',
      url='http://lojikil.com/p/chasha',
      py_modules=['chasha'],
      scripts=['chasha.py'],
      license='MIT',
      platforms='any',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Internet :: Gopher'])
