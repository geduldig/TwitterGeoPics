"""
	REQUIRED: PASTE YOUR TWITTER OAUTH CREDENTIALS INTO puttytat/credentials.txt 
	          OR USE -oauth OPTION TO USE A DIFFERENT FILE CONTAINING THE CREDENTIALS.
	
	Downloads old tweets from the newest to the oldest that contain any of the words 
	that are passed as arguments on the command line.  Prints the tweet text and URLs 
	of any embedded photos.

	Use the -photo_dir option to save photos to a directory.
	
	Use the -stalk flag to print latitude and longitude from Google's Map service.
	Location is determined from either the user's profile or geocode.
	
	Use the -location to get tweets from a geographical region.  If you want to 
	override the default radius (in km) use the -radius option.  
	
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
		for media in status['entities'].get('media'):
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
							print>>sys.stderr, 'GEOCODER QUOTA EXCEEDED:', GEO.count_request
				photo_url = media['media_url_https']
				if photo_dir:
					print media['id_str']
					file_name = os.path.join(photo_dir, media['id_str']) + '.' + photo_url.split('.')[-1]
					urllib.urlretrieve(photo_url, file_name)


def search_tweets(list, wait, photo_dir, region, stalk):
	"""Get tweets containing any words in 'list' and that have location or coordinates in 'region'
	
	"""
	words = ' OR '.join(list)
	params = { 'q': words }
	if region:
		params['geocode'] = '%f,%f,%fkm' % region # lat,lng,radius
	while True:
		tw = puttytat.TwitterRestPager(OAUTH)
		for item in tw.request('search/tweets', params, wait):
			if 'text' in item:
				parse_tweet(item, photo_dir, stalk)
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
	parser.add_argument('-photo_dir', metavar='DIRECTORYNAME', type=str, help='download photos to this directory')
	parser.add_argument('-location', type=str, help='limit tweets to a place')
	parser.add_argument('-radius', type=str, help='distance from "location" in km')
	parser.add_argument('-stalk', action='store_true', help='print tweet location')
	parser.add_argument('words', metavar='W', type=str, nargs='+', help='word(s) to search')
	args = parser.parse_args()	

	OAUTH = puttytat.TwitterOauth.read_file(args.oauth)
	
	try:
		if args.location:
			lat, lng, radius = GEO.get_region_circle(args.location)
			print 'Google found region at %f,%f with a radius of %s km' % (lat, lng, radius)
			if args.radius:
				radius = args.radius
			region = (lat, lng, radius)
		else:
			region = None
		search_tweets(args.words, args.wait, args.photo_dir, region, args.stalk)
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
	except Exception, e:
		print>>sys.stderr, '*** STOPPED', e
		
	GEO.print_stats()