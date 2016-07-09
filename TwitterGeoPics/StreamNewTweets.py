__author__ = "geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

import argparse
import codecs
from .Geocoder import Geocoder
import os
import sys
from TwitterAPI import TwitterAPI, TwitterOAuth
import urllib


GEO = Geocoder()


def download_photo(status, photo_dir):
	"""Download photo(s) from embedded url(s)."""
	if 'media' in status['entities']:
		for media in status['entities'].get('media'):
			if media['type'] == 'photo':
				photo_url = media['media_url_https']
				screen_name = status['user']['screen_name']
				file_name = os.path.join(photo_dir, screen_name) + '.' + photo_url.split('.')[-1]
				urllib.urlretrieve(photo_url, file_name)


def lookup_geocode(status):
	"""Get geocode either from tweet's 'coordinates' field (unlikely) or from tweet's location and Google."""
	if not GEO.quota_exceeded:
		try:
			geocode = GEO.geocode_tweet(status)
			if geocode[0]:
				print('GEOCODE: %s %s,%s' % geocode)
		except Exception as e:
			if GEO.quota_exceeded:
				print('GEOCODER QUOTA EXCEEDED: %s' % GEO.count_request)


def process_tweet(status, photo_dir, stalk):
	print('\n%s: %s' % (status['user']['screen_name'], status['text']))
	print(status['created_at'])
	if photo_dir:
		download_photo(status, photo_dir)
	if stalk:
		lookup_geocode(status)
					

def stream_tweets(api, word_list, photo_dir, region, stalk, no_retweets):
	"""Get tweets containing any words in 'word_list' or that originate from 'region'."""
	params = {}
	if word_list is not None:
		words = ','.join(word_list)
		params['track'] = words
	if region is not None:
		params['locations'] = '%f,%f,%f,%f' % region
		print('REGION %s' % str(region))
	while True:
		try:
			r = api.request('statuses/filter', params)
			while True:
				for item in r.get_iterator():
					if 'text' in item:
						if not no_retweets or not item.has_key('retweeted_status'):
							process_tweet(item, photo_dir, stalk)
					elif 'disconnect' in item:
						raise Exception('Disconnect: %s' % item['disconnect'].get('reason'))
		except Exception as e:
			# reconnect on 401 errors and socket timeouts
			print('*** MUST RECONNECT %s\n' % e)
			

if __name__ == '__main__':
	# print UTF-8 to the console
	try:
		# python 3
		sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
	except:
		# python 2
		sys.stdout = codecs.getwriter('utf8')(sys.stdout)

	parser = argparse.ArgumentParser(description='Get real-time tweet stream with embedded pics and/or geocode.')
	parser.add_argument('-location', type=str, help='limit tweets to a place; use ALL to get all geocoded tweets')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-no_retweets', action='store_true', help='exclude re-tweets')
	parser.add_argument('-photo_dir', metavar='DIRECTORYNAME', type=str, help='download photos to this directory')
	parser.add_argument('-stalk', action='store_true', help='print tweet location')
	parser.add_argument('-words', metavar='W', type=str, nargs='+', help='word(s) to track')
	args = parser.parse_args()	

	if args.words is None and args.location is None:
		sys.exit('You must use either -words or -locoation or both.')

	oauth = TwitterOAuth.read_file(args.oauth)
	api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)
	
	try:
		if args.location:
			if args.location.lower() == 'all':
				region = (-180, -90, 180, 90)
			else:
				latC, lngC, latSW, lngSW, latNE, lngNE = GEO.get_region_box(args.location)
				region = (lngSW, latSW, lngNE, latNE)
			print('Google found region at %f,%f and %f,%f' % region)
		else:
			region = None
		stream_tweets(api, args.words, args.photo_dir, region, args.stalk, args.no_retweets)
	except KeyboardInterrupt:
		print('\nTerminated by user\n')
		
	GEO.print_stats()
