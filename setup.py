from distutils.core import setup

setup(
    name='TwitterGeoPics',
    version='2.0.3',
    author='Jonas Geduldig',
    author_email='boxnumber03@gmail.com',
    packages=['TwitterGeoPics'],
    package_data={'': []},
    url='https://github.com/geduldig/TwitterGeoPics',
    download_url = 'https://github.com/gedldig/TwitterGeoPics/tarball/master',
    license='MIT',
    keywords='twitter, geocode',
    description='Command line scripts for geocoding tweets from twitter.com and for downloading embedded photos.',
    install_requires = ['TwitterAPI', 'fridge']
)
