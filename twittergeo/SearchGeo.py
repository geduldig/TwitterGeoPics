"""
	REQUIRED: PASTE YOUR TWITTER OAUTH CREDENTIALS INTO twittergeo/credentials.txt 
	          OR USE -oauth OPTION TO USE A DIFFERENT FILE CONTAINING THE CREDENTIALS.
	
	Downloads old tweets from the newest to the oldest that contain any of the words 
	that are passed as arguments on the command line.  Prints the tweet text and 
	location information, including latitude and longitude from Google's Map service.
	
	Use the -location option to get tweets from a geographical region.  If you want to 
	override the default radius (in km) use the -radius option.  Location is 
	determined from either the user's profile or geocode.
	
	The script calls Twitter's REST API which permits about a week's worth of old 
	tweets to be downloaded before breaking the connection.  Twitter may also 
	disconnect if you exceed 180 downloads per 15 minutes.  For this reason sleep is 
	called after each request.  The default is 5 seconds.  Override with the '-wait' 
	option.
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

def parse_tweet(status):
	"""Print tweet, location and geocode
	
	"""
	try:
		geocode = GEO.geocode_tweet(status)
		print '\n%s: %s' % (status['user']['screen_name'], status['text'])
		print 'LOCATION:', status['user']['location']
		print 'GEOCODE:', geocode
	except Exception, e:
		if GEO.quota_exceeded:
			raise

def search_tweets(list, wait, region):
	"""Get tweets containing any words in 'list' and that have location or coordinates in 'region'
	
	"""
	words = ' OR '.join(list)
	params = { 'q': words }
	if region:
		params['geocode'] = '%f,%f,%fkm' % region # lat,lng,radius
	search = twitterapi.TwSearch(OAUTH, params)
	while True:
		for item in search.past_results(wait):
			if 'text' in item:
				parse_tweet(item)
			elif 'message' in item:
				if item['code'] == 131:
					continue # ignore internal server error
				elif item['code'] == 88:
					print>>sys.stderr, 'Suspend search until %s' % search.get_quota()['reset']
				raise Exception('Message from twiter: %s' % item['message'])
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Search tweet history.')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-wait', type=int, default=5, help='seconds to wait between searches')
	parser.add_argument('-location', type=str, help='limit tweets to a place')
	parser.add_argument('-radius', type=float, help='distance from "location" in km')
	parser.add_argument('words', metavar='W', type=str, nargs='+', help='word(s) to search')
	args = parser.parse_args()	

	if args.oauth:
		OAUTH = twitterapi.TwCredentials.read_file(args.oauth)
	else:
		path = os.path.dirname(__file__)
		path = os.path.join(path, 'credentials.txt')
		OAUTH = twitterapi.TwCredentials.read_file(path)
	
	try:
		if args.location:
			lat, lng, radius = GEO.get_region_circle(args.location)
			print 'Google found region at %f,%f with a radius of %s km' % (lat, lng, radius)
			if args.radius:
				radius = args.radius
			region = (lat, lng, radius)
		else:
			region = None
		search_tweets(args.words, args.wait, region)
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
	except Exception, e:
		print>>sys.stderr, '*** STOPPED', e
		
	GEO.print_stats()