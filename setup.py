from distutils.core import setup

setup(
    name='TwitterGeo',
    version='1.0.0',
    author='Jonas Geduldig',
    author_email='boxnumber03@gmail.com',
    packages=['twittergeo'],
    package_data={'': ['credentials.txt']},
    url='https://github.com/geduldig/twittergeo',
    download_url = 'https://github.com/gedldig/twittergeo/tarball/1.0.0',
    license='MIT',
    keywords='twitter',
    description='Command line scripts for geocoding old and new tweets from twitter.com and for downloading embedded photos.',
    long_description=open('README.txt').read(),
    install_requires = ['twitterapi', 'pygeocoder', 'Fridge']
)