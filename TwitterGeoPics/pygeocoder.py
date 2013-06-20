#!/usr/bin/env python
#
# Xiao Yu - Montreal - 2010
# Based on googlemaps by John Kleint
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Python wrapper for Google Geocoding API V3.

* **Geocoding**: convert a postal address to latitude and longitude
* **Reverse Geocoding**: find the nearest address to coordinates

"""

import requests
import functools
import base64
import hmac
import hashlib
from pygeolib import GeocoderError, GeocoderResult
#from __version__ import VERSION

try:
    import json
except ImportError:
    import simplejson as json

__all__ = ['Geocoder', 'GeocoderError', 'GeocoderResult']


# this decorator lets me use methods as both static and instance methods
class omnimethod(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return functools.partial(self.func, instance)


class Geocoder(object):
    """
    A Python wrapper for Google Geocoding V3's API

    """

    GEOCODE_QUERY_URL = 'https://maps.google.com/maps/api/geocode/json?'

    def __init__(self, client_id=None, private_key=None):
        """
        Create a new :class:`Geocoder` object using the given `client_id` and
        `referrer_url`.

        :param client_id: Google Maps Premier API key
        :type client_id: string

        Google Maps API Premier users can provide his key to make 100,000 requests
        a day vs the standard 2,500 requests a day without a key

        """
        self.client_id = client_id
        self.private_key = private_key

    @omnimethod
    def get_data(self, params={}):
        """
        Retrieve a JSON object from a (parameterized) URL.

        :param params: Dictionary mapping (string) query parameters to values
        :type params: dict
        :return: JSON object with the data fetched from that URL as a JSON-format object.
        :rtype: (dict or array)

        """
        request = requests.Request('GET',
                url = Geocoder.GEOCODE_QUERY_URL,
                params = params,
                headers = {
                    'User-Agent': 'pygeocoder/' + VERSION + ' (Python)'
                })

        if self and self.client_id and self.private_key:
            self.add_signature(request)

        response = requests.Session().send(request.prepare())
        if response.status_code == 403:
            raise GeocoderError("Forbidden, 403", response.url)
        response_json = response.json()

        if response_json['status'] != GeocoderError.G_GEO_OK:
            raise GeocoderError(response_json['status'], response.url)
        return response_json['results']

    @omnimethod
    def add_signature(self, request):
        decoded_key = base64.urlsafe_b64decode(str(self.private_key))
        signature = hmac.new(decoded_key, request.url, hashlib.sha1)
        encoded_signature = base64.urlsafe_b64encode(signature.digest())
        request.params['client'] = str(self.client_id)
        request.params['signature'] = encoded_signature

    @omnimethod
    def geocode(self, address, sensor='false', bounds='', region='', language=''):
        """
        Given a string address, return a dictionary of information about
        that location, including its latitude and longitude.

        :param address: Address of location to be geocoded.
        :type address: string
        :param sensor: ``'true'`` if the address is coming from, say, a GPS device.
        :type sensor: string
        :param bounds: The bounding box of the viewport within which to bias geocode results more prominently.
        :type bounds: string
        :param region: The region code, specified as a ccTLD ("top-level domain") two-character value for biasing
        :type region: string
        :param language: The language in which to return results.
        :type language: string
        :returns: `geocoder return value`_ dictionary
        :rtype: dict
        :raises GeocoderError: if there is something wrong with the query.

        For details on the input parameters, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingRequests

        For details on the output, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingResponses

        """

        params = {
            'address':  address,
            'sensor':   sensor,
            'bounds':   bounds,
            'region':   region,
            'language': language,
        }
        if self is not None:
            return GeocoderResult(self.get_data(params=params))
        else:
            return GeocoderResult(Geocoder.get_data(params=params))

    @omnimethod
    def reverse_geocode(self, lat, lng, sensor='false', bounds='', region='', language=''):
        """
        Converts a (latitude, longitude) pair to an address.

        :param lat: latitude
        :type lat: float
        :param lng: longitude
        :type lng: float
        :return: `Reverse geocoder return value`_ dictionary giving closest
            address(es) to `(lat, lng)`
        :rtype: dict
        :raises GeocoderError: If the coordinates could not be reverse geocoded.

        Keyword arguments and return value are identical to those of :meth:`geocode()`.

        For details on the input parameters, visit
        http://code.google.com/apis/maps/documentation/geocoding/#GeocodingRequests

        For details on the output, visit
        http://code.google.com/apis/maps/documentation/geocoding/#ReverseGeocoding

        """
        params = {
            'latlng':   "%f,%f" % (lat, lng),
            'sensor':   sensor,
            'bounds':   bounds,
            'region':   region,
            'language': language,
        }

        if self is not None:
            return GeocoderResult(self.get_data(params=params))
        else:
            return GeocoderResult(Geocoder.get_data(params=params))

if __name__ == "__main__":
    import sys
    from optparse import OptionParser

    def main():
        """
        Geocodes a location given on the command line.

        Usage:
            pygeocoder.py "1600 amphitheatre mountain view ca" [YOUR_API_KEY]
            pygeocoder.py 37.4219720,-122.0841430 [YOUR_API_KEY]

        When providing a latitude and longitude on the command line, ensure
        they are separated by a comma and no space.

        """
        usage = "usage: %prog [options] address"
        parser = OptionParser(usage, version=VERSION)
        parser.add_option("-k", "--key", dest="key", help="Your Google Maps API key")
        (options, args) = parser.parse_args()

        if len(args) != 1:
            parser.print_usage()
            sys.exit(1)

        query = args[0]
        gcoder = Geocoder(options.key)

        try:
            result = gcoder.geocode(query)
        except GeocoderError as err:
            sys.stderr.write('%s\n%s\nResponse:\n' % (err.url, err))
            json.dump(err.response, sys.stderr, indent=4)
            sys.exit(1)

        print(result)
        print(result.coordinates)
    main()
