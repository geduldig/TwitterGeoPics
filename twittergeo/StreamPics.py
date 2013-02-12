"""
	REQUIRED: PASTE YOUR TWITTER OAUTH CREDENTIALS INTO puttytat/credentials.txt 
	          OR USE -oauth OPTION TO USE A DIFFERENT FILE CONTAINING THE CREDENTIALS.
	
	Downloads real-time tweets that contain embedded photo URLs.  You must supply 
	either one or both of the -words and -location options.  Prints the tweet text, 
	location information, including latitude and longitude from Google's Map service,
	and all photo URLs.

	Use the -words option to get tweets that contain any of the words that are passed 
	as arguments on the command line.
		
	Use the -location option to get tweets from a geographical region.  Location is 
	determined only from geocode in the tweet.  Use -location ALL to get all geocoded 
	tweets from any location.
	
	Use the -photo_dir option to save photos to a directory.
	
	Use the -stalk flag to print latitude and longitude from Google's Map service.
	
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
import puttytat
import urllib

OAUTH = None
GEO = Geocoder.Geocoder()


def parse_tweet(status, photo_dir, stalk):
	"""If tweet contains photo, print tweet.
	   If stalking, print location and geocode.
	   If photo_dir, print photo id and save photo to file.
	
	"""
	if 'media' in status['entities']:
		photo_count = 0
		for media in  status['entities'].get('media'):
			if media['type'] == 'photo':
				photo_count += 1
				if photo_count == 1:
					print '\n%s: %s' % (status['user']['screen_name'], status['text'])
				if stalk and not GEO.quota_exceeded:
					try:
						geocode = GEO.geocode_tweet(status)
						print 'LOCATION:', status['user']['location']
						print 'GEOCODE:', geocode
					except Exception, e:
						if GEO.quota_exceeded:
							print>>sys.stderr, '*** GEOCODER QUOTA EXCEEDED:', GEO.count_request
				photo_url = media['media_url_https']
				if photo_dir:
					print media['id_str']
					file_name = os.path.join(photo_dir, media['id_str']) + '.' + photo_url.split('.')[-1]
					urllib.urlretrieve(photo_url, file_name)
					

def stream_tweets(list, photo_dir, region, stalk):
	"""Get tweets containing any words in 'list' or that have location or coordinates in 'region'
	
	"""
	params = {}
	if list is not None:
		words = ','.join(list)
		params['track'] = words
	if region is not None:
		params['locations'] = '%f,%f,%f,%f' % region
		print 'REGION', region
	while True:
		tw = puttytat.TwitterStream(OAUTH)
		try:
			while True:
				for item in tw.request('statuses/filter', params):
					if 'text' in item:
						parse_tweet(item, photo_dir, stalk)
					elif 'disconnect' in item:
						raise Exception('Disconnect: %s' % item['disconnect'].get('reason'))
		except Exception, e:
			# reconnect on 401 errors and socket timeouts
			print>>sys.stderr, '*** MUST RECONNECT', e
			

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Get real-time tweet stream.')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-location', type=str, help='limit tweets to a place; use ALL to get all geocoded tweets')
	parser.add_argument('-photo_dir', metavar='DIRECTORYNAME', type=str, help='download photos to this directory')
	parser.add_argument('-stalk', action='store_true', help='print tweet location')
	parser.add_argument('-words', metavar='W', type=str, nargs='+', help='word(s) to track')
	args = parser.parse_args()	

	if args.words is None and args.location is None:
		sys.exit('You must use either -words or -locoation or both.')

	OAUTH = puttytat.TwitterOauth.read_file(args.oauth)

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
		stream_tweets(args.words, args.photo_dir, region, args.stalk)
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
		
	GEO.print_stats()