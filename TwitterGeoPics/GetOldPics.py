__author__ = "Jonas Geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

import argparse
from .Geocoder import Geocoder
import os
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRestPager
import urllib


GEO = Geocoder()


def parse_tweet(status, photo_dir, stalk):
	"""Use only tweets that embed photos."""
	if 'media' in status['entities']:
		photo_count = 0
		for media in status['entities'].get('media'):
			if media['type'] == 'photo':
				photo_count += 1
				if photo_count == 1:
					print('\n%s: %sprint' % (status['user']['screen_name'], status['text']))
				if stalk and not GEO.quota_exceeded:
					try:
						geocode = GEO.geocode_tweet(status)
						print('LOCATION: %s' % status['user']['location'])
						print('GEOCODE: %s' % geocode)
					except Exception as e:
						if GEO.quota_exceeded:
							print('GEOCODER QUOTA EXCEEDED: %s' % GEO.count_request)
				if photo_dir:
					photo_url = media['media_url_https']
					screen_name = status['user']['screen_name']
					file_name = os.path.join(photo_dir, screen_name) + '.' + photo_url.split('.')[-1]
					urllib.urlretrieve(photo_url, file_name)
					print(screen_name)


def search_tweets(api, list, photo_dir, region, stalk, no_retweets):
	"""Get tweets containing any words in 'list' and that have location or coordinates in 'region'."""
	words = ' OR '.join(list)
	params = { 'q': words }
	if region:
		params['geocode'] = '%f,%f,%fkm' % region # lat,lng,radius
	while True:
		pager = TwitterRestPager(api, 'search/tweets', params)
		for item in pager.get_iterator():
			if 'text' in item:
				if not no_retweets or not item.has_key('retweeted_status'):
					parse_tweet(item, photo_dir, stalk)
			elif 'message' in item:
				if item['code'] == 131:
					continue # ignore internal server error
				elif item['code'] == 88:
					print('Suspend search until %s' % search.get_quota()['reset'])
				raise Exception('Message from twiter: %s' % item['message'])
		
			
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Search tweet history.')
	parser.add_argument('-location', type=str, help='limit tweets to a place')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-no_retweets', action='store_true', help='exclude re-tweets')
	parser.add_argument('-photo_dir', metavar='DIRECTORYNAME', type=str, help='download photos to this directory')
	parser.add_argument('-radius', type=str, help='distance from "location" in km')
	parser.add_argument('-stalk', action='store_true', help='print tweet location')
	parser.add_argument('words', metavar='W', type=str, nargs='+', help='word(s) to search')
	args = parser.parse_args()	

	oauth = TwitterOAuth.read_file(args.oauth)
	api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)
	
	try:
		if args.location:
			lat, lng, radius = GEO.get_region_circle(args.location)
			print('Google found region at %f,%f with a radius of %s km' % (lat, lng, radius))
			if args.radius:
				radius = args.radius
			region = (lat, lng, radius)
		else:
			region = None
		search_tweets(api, args.words, args.photo_dir, region, args.stalk, args.no_retweets)
	except KeyboardInterrupt:
		print('\nTerminated by user\n')
	except Exception as e:
		print('*** STOPPED %s\n' % e)
		
	GEO.print_stats()