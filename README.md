[![Downloads](https://pypip.in/d/TwitterGeoPics/badge.png)](https://crate.io/packages/TwitterGeoPics)
[![Downloads](https://pypip.in/v/TwitterGeoPics/badge.png)](https://crate.io/packages/TwitterGeoPics)

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
The geocoder uses Google Maps API to get latitude and longitude from a human-readable address. 

All geocode is cached to avoid duplicate requests.  Geocode requests are throttled to avoid exceeding the rate limit.  See Geocoder.py for more information.

Dependencies
-----------
* TwitterAPI
* pygeocoder
* Fridge
