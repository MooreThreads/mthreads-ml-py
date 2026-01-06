from distutils.core import setup
from sys import version
from sys import exit

# earlier versions don't support all classifiers
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

_package_name='mthreads-ml-py'

long_description = None
try:
    # Trying the more correct python3 approach for finding the readme.
    # This will fail with an import error on earlier version of python3 and python2
    # Code is from https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/
    from pathlib import Path
    this_dir = Path(__file__).parent
    long_description = (this_dir / 'README.md').read_text()
except ImportError:
    # If pathlib can not find the readme, try reading it from the current dir.
    # This should always work if the readme is in the parent directory.
    # This will also work with python2.
    try:
        with open('README.md', 'r') as readme:
            long_description = readme.read()
    except IOError:
        # The python2 error for files that don't exist.
        # Python3 translates this to an OSError.
        pass
    except FileNotFoundError:
        # The Python3 error for files that don't exist.
        # Catching this second since it doesn't exist in python 2
        pass
finally:
    # Exit if there is no long description.
    if long_description is None:
        print('Unable to load README.md as long description.')
        print('Make sure it is in the correct directory.')
        exit(1)


setup(name=_package_name,
      version='2.2.9',
      description='Python Bindings for the Moore Threads GPU Management Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      py_modules=['pymtml', 'example'],
      package_data={_package_name: ['Example.txt']},
      license='MIT',
      url='https://developer.mthreads.com',
      author='Moore Threads Corporation',
      author_email='mt-sw-cloudcomputing@mthreads.com',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Hardware',
          'Topic :: System :: Systems Administration',
          ],
      )
