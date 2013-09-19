__author__ = "Jonas Geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

import argparse
from .Geocoder import Geocoder
from TwitterAPI import TwitterAPI, TwitterOAuth, TwitterRestPager


GEO = Geocoder()


def parse_tweet(status):
	"""Print tweet, location and geocode."""
	try:
		geocode = GEO.geocode_tweet(status)
		print('\n%s: %s' % (status['user']['screen_name'], status['text']))
		print('LOCATION: %s' % status['user']['location'])
		print('GEOCODE: %s' % geocode)
	except Exception as e:
		if GEO.quota_exceeded:
			raise


def search_tweets(api, list, region):
	"""Get tweets containing any words in 'list' and that have location or coordinates in 'region'."""
	words = ' OR '.join(list)
	params = { 'q': words }
	if region:
		params['geocode'] = '%f,%f,%fkm' % region # lat,lng,radius
	while True:
		pager = TwitterRestPager(api, 'search/tweets', params)
		for item in pager.get_iterator():
			if 'text' in item:
				parse_tweet(item)
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
	parser.add_argument('-radius', type=float, help='distance from "location" in km')
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
		search_tweets(api, args.words, region)
	except KeyboardInterrupt:
		print('\nTerminated by user\n')
	except Exception as e:
		print('*** STOPPED %s\n' % e)
		
	GEO.print_stats()