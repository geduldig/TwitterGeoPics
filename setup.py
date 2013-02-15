from distutils.core import setup

setup(
    name='TwitterGeo',
    version='1.1.0',
    author='Jonas Geduldig',
    author_email='boxnumber03@gmail.com',
    packages=['twittergeo'],
    package_data={'': ['credentials.txt', 'geocode.cache']},
    url='https://github.com/geduldig/twittergeo',
    download_url = 'https://github.com/gedldig/twittergeo/tarball/master',
    license='MIT',
    keywords='twitter',
    description='Command line scripts for geocoding old and new tweets from twitter.com and for downloading embedded photos.',
    install_requires = ['puttytat', 'pygeocoder', 'fridge']
)
