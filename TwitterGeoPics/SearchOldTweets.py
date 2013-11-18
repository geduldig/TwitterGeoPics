__author__ = "Jonas Geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

import argparse
import codecs
from .Geocoder import Geocoder
import os
import sys
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRestPager
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


def search_tweets(api, word_list, photo_dir, region, stalk, no_retweets, count):
	"""Get tweets containing any words in 'word_list'."""
	words = ' OR '.join(word_list)
	params = {'q':words, 'count':count}
	if region:
		params['geocode'] = '%f,%f,%fkm' % region # lat,lng,radius
	while True:
		pager = TwitterRestPager(api, 'search/tweets', params)
		for item in pager.get_iterator():
			if 'text' in item:
				if not no_retweets or not item.has_key('retweeted_status'):
					process_tweet(item, photo_dir, stalk)
			elif 'message' in item:
				if item['code'] == 131:
					continue # ignore internal server error
				elif item['code'] == 88:
					print('Suspend search until %s' % search.get_quota()['reset'])
				raise Exception('Message from twitter: %s' % item['message'])
		
			
if __name__ == '__main__':
	# print UTF-8 to the console
	try:
		# python 3
		sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
	except:
		# python 2
		sys.stdout = codecs.getwriter('utf8')(sys.stdout)

	parser = argparse.ArgumentParser(description='Search tweet history for pics and/or geocode.')
	parser.add_argument('-count', type=int, default=15, help='download batch size')
	parser.add_argument('-location', type=str, help='limit tweets to a place')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-no_retweets', action='store_true', help='exclude re-tweets')
	parser.add_argument('-photo_dir', metavar='DIRECTORYNAME', type=str, help='download photos to this directory')
	parser.add_argument('-stalk', action='store_true', help='print tweet location')
	parser.add_argument('-words', metavar='W', type=str, nargs='+', help='word(s) to search')
	args = parser.parse_args()	

	if args.words is None:
		sys.exit('You must use -words.')

	oauth = TwitterOAuth.read_file(args.oauth)
	api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)
	
	try:
		if args.location:
			lat, lng, radius = GEO.get_region_circle(args.location)
			region = (lat, lng, radius)
			print('Google found region at %f,%f with a radius of %s km' % (lat, lng, radius))
		else:
			region = None
		search_tweets(api, args.words, args.photo_dir, region, args.stalk, args.no_retweets, args.count)
	except KeyboardInterrupt:
		print('\nTerminated by user\n')
	except Exception as e:
		print('*** STOPPED %s\n' % e)
		
	GEO.print_stats()
