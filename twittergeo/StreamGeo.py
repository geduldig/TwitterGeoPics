"""
	REQUIRED: PASTE YOUR TWITTER OAUTH CREDENTIALS INTO twittergeo/credentials.txt 
	          OR USE -oauth OPTION TO USE A DIFFERENT FILE CONTAINING THE CREDENTIALS.
	
	Downloads real-time tweets.  You must supply either one or both of the -words and
	-location options.  Prints the tweet text and location information, including 
	latitude and longitude from Google's Map service.

	Use the -words option to get tweets that contain any of the words that are passed 
	as arguments on the command line.
		
	Use the -location option to get tweets from a geographical region.  Location is 
	determined only from geocode in the tweet.  Use -location ALL to get all geocoded 
	tweets from any location.
	
	The script calls Twitter's Streaming API which is bandwidth limitted.  If you 
	exceed the rate limit, Twitter sends a message with the total number of tweets 
	skipped during the current connection.  This number is printed, and the connection 
	remains open.
"""

__author__ = "Jonas Geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

# unicode printing for Windows 
import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import argparse
import Geocoder
import os
import twitterapi
import urllib

OAUTH = None
GEO = Geocoder.Geocoder()

def parse_tweet(status, region):
	"""Print tweet, location and geocode
	
	"""
	try:
		geocode = GEO.geocode_tweet(status)
		print '\n%s: %s' % (status['user']['screen_name'], status['text'])
		print 'LOCATION:', status['user']['location']
		print 'GEOCODE:', geocode
	except Exception, e:
		if GEO.quota_exceeded:
			print>>sys.stderr, '*** GEOCODER QUOTA EXCEEDED:', GEO.count_request
			raise

def stream_tweets(list, region):
	"""Get tweets containing any words in 'list' or that have location or coordinates in 'region'
	
	"""
	params = {}
	if list != None:
		words = ','.join(list)
		params['track'] = words
	if region != None:
		params['locations'] = '%f,%f,%f,%f' % region
		print 'REGION', region
	while True:
		try:
			stream = twitterapi.TwStream(OAUTH, params)
			while True:
				for item in stream.results():
					if 'text' in item:
						parse_tweet(item, region)
					elif 'disconnect' in item:
						raise Exception('Disconnect: %s' % item['disconnect'].get('reason'))
		except Exception, e:
			# reconnect on 401 errors and socket timeouts
			print>>sys.stderr, '*** MUST RECONNECT', e

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Get real-time tweet stream.')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-location', type=str, help='limit tweets to a place; use ALL to get all geocoded tweets')
	parser.add_argument('-words', metavar='W', type=str, nargs='+', help='word(s) to track')
	args = parser.parse_args()	

	if args.words == None and args.location == None:
		sys.exit('You must use either -words or -locoation or both.')

	if args.oauth:
		OAUTH = twitterapi.TwCredentials.read_file(args.oauth)
	else:
		path = os.path.dirname(__file__)
		path = os.path.join(path, 'credentials.txt')
		OAUTH = twitterapi.TwCredentials.read_file(path)

	if args.location:
		if args.location.lower() == 'all':
			region = (-180, -90, 180, 90)
		else:
			latC, lngC, latSW, lngSW, latNE, lngNE = GEO.get_region_box(args.location)
			region = (lngSW, latSW, lngNE, latNE)
			print 'Google found region at %f,%f and %f,%f' % region
	else:
		region = None
	
	try:
		stream_tweets(args.words, region)
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
				
	GEO.print_stats()