from distutils.core import setup
import TwitterGeoPics
import io

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

setup(
    name='TwitterGeoPics',
    version=TwitterGeoPics.__version__,
    author='geduldig',
    author_email='boxnumber03@gmail.com',
    packages=['TwitterGeoPics'],
    package_data={'': []},
    url='https://github.com/geduldig/TwitterGeoPics',
    download_url = 'https://github.com/gedldig/TwitterGeoPics/tarball/master',
    license='MIT',
    keywords='twitter, geocode',
    description='Command line scripts for geocoding tweets from twitter.com and for downloading embedded photos.',
    install_requires = ['TwitterAPI>=2.1', 'pygeocoder', 'fridge', 'tzwhere']
)
