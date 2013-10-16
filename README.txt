TwitterGeoPics
==============
Python scripts for geocoding tweets and for downloading images embedded in tweets.  Supports Python 2.x and 3.x.

SearchOldTweets.py
-----------------
Uses 'search/tweets' Twitter resource to get tweets, geocode and embedded photos.

Example:

	> python -u -m TwitterGeoPics.SearchOldTweets -words love hate -location nyc

For help:

	> python -u -m TwitterGeoPics.SearchOldTweets -h

StreamNewTweets.py
-----------------
Uses 'statuses/filter' Twitter resource to get tweets, geocode and embedded photos.

Example:

	> python -u -m TwitterGeoPics.StreamNewTweets -words love hate -location nyc

For help:

	> python -u -m TwitterGeoPics.StreamNewTweets -h
	
Authentication
--------------
See TwitterAPI documentation.

Geocoder
--------
The geocoder uses Google Maps API to get latitude and longitude from a human-readable address.  See pygeocoder package for details.  Google will attempt to geocode anything.  (If you say your location is The Titanic, Google will geocode the shipwreck.)

All geocode is cached to avoid duplicate requests.  Geocode requests are throttled to avoid exceeding the rate limit.  See Geocoder.py for more information.

Dependencies
-----------
* TwitterAPI
* pygeocoder
* Fridge

Contributors
------------
* Jonas Geduldig
