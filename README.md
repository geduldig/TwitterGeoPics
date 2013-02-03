# TwitterGeo #

_Scripts for geocoding tweets and for downloading images embedded in tweets._

### Getting Location and Embedded Images... ###

TwitterGeo contains command line scripts for geocoding tweets and extracting embedded images from tweets from twitter.com.  The scripts take one or more search words as command line arguments.  The scripts download old tweets using Twitter's REST API and download new tweets using Twitter's Streaming API.

About 1% or 2% of tweets contain latitude and longitude.  Of those tweets that do not contain coordinate data, about 60% have the user's profile location, a descriptive text field that may or not be accurate.  Using Google's Maps API, we can geocode these tweets, which locates about half of all tweets, a portion of which are suspect.

Use the location option to restrict searches to a geographic location.  Twitter returns tweets that either contain coordinates in the location region or tweets from users whose profile location is in the specified region.  

Google does not require autentication, but it does enforce a daily limit of about 2,500 requests per day and about 10 requests per second.

The Twitter API requires OAuth credentials which you can get by creating an application on dev.twitter.com.  Once you have your OAuth secrets and keys, copy them into twittergeo/credentials.txt.  Alternatively, specify the credentials file on the command line.

Twitter restricts searching old tweets to within roughly the past week.  Twitter also places a bandwidth limit on searching current tweet, but you will notice this only when you are searching a popular word.  When this limit occurs the total number of skipped tweets is printed and the connection is maintained.

### Features ###

*The following modules run as command line scripts and write tweets to the console.*  

***SearchGeo***

Prints old tweets and their location information and coordinates when possible.

***StreamGeo***

Prints new tweets and their location information and coordinates when possible.

***SearchPics***

Prints old tweets, their coordinates and URLs of any embedded photos.  To download the photos use the -photo_dir option.  To get tweets only from a specific geographic region use the -location.

***StreamPics***

Prints new tweets, their coordinates and URLs of any embedded photos.  To download the photos use the -photo_dir option.  To get tweets only from a specific geographic region use the -location.

*This is utility module.*

***Geocoder***

A wrapper for the pygeocoder package.  It adds throttling to respect Google's daily quota and rate limit.  It also provides a caching mechanism for storing geocode lookups to a text file.  The caching is only partially effective because user can enter their location in any format.  There are also some Twitter specific methods.

### Installation ###


1. On a command line, type:

		pip install twittergeo

2. Either copy your OAuth consumer secret and key and your access token secret and key into twittergeo/credentials.txt, or copy them into another file which you will specify on the command line.  See credentials.txt for the expected file format.

3. Run a script type with '-m' option, for example:

		python -m twittergeo.StreamGeo zzz
		python -m twittergeo.StreamGeo zzz -oauth ./my_credentials.txt

### External Dependencies ###

This package uses the following external packages.

* twitterapi - for downloading tweets
* pygeocoder - for geo-referencing using Google's Maps service
* fridge - for caching latitudes and longitudes in a persistant dict

### Contributors ###

Jonas Geduldig