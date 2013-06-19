__author__ = "Jonas Geduldig"
__date__ = "December 20, 2012"
__license__ = "MIT"

import argparse
from Geocoder import Geocoder
import sys
from TwitterAPI import TwitterAPI, TwitterOAuth


GEO = Geocoder()


def parse_tweet(status, region):
	"""Print tweet, location and geocode."""
	try:
		geocode = GEO.geocode_tweet(status)
		sys.stdout.write('\n%s: %s\n' % (status['user']['screen_name'], status['text']))
		sys.stdout.write('LOCATION: %s\n' % status['user']['location'])
		sys.stdout.write('GEOCODE: %s\n' % geocode)
	except Exception as e:
		if GEO.quota_exceeded:
			sys.stderr.write('*** GEOCODER QUOTA EXCEEDED: %s\n' % GEO.count_request)
			raise


def stream_tweets(api, list, region):
	"""Get tweets containing any words in 'list' or that have location or coordinates in 'region'."""
	params = {}
	if list is not None:
		words = ','.join(list)
		params['track'] = words
	if region is not None:
		params['locations'] = '%f,%f,%f,%f' % region
		sys.stdout.write('REGION %s\n' % region)
	while True:
		try:
			api.request('statuses/filter', params)
			iter = api.get_iterator()
			while True:
				for item in iter:
					if 'text' in item:
						parse_tweet(item, region)
					elif 'disconnect' in item:
						raise Exception('Disconnect: %s' % item['disconnect'].get('reason'))
		except Exception as e:
			# reconnect on 401 errors and socket timeouts
			sys.stderr.write('*** MUST RECONNECT %s\n' % e)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Get real-time tweet stream with geocode.')
	parser.add_argument('-location', type=str, help='limit tweets to a place; use ALL to get all geocoded tweets')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='read OAuth credentials from file')
	parser.add_argument('-words', metavar='W', type=str, nargs='+', help='word(s) to track')
	args = parser.parse_args()	

	if args.words is None and args.location is None:
		sys.exit('You must use either -words or -locoation or both.')

	oauth = TwitterOAuth.read_file(args.oauth)
	api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)

	if args.location:
		if args.location.lower() == 'all':
			region = (-180, -90, 180, 90)
		else:
			latC, lngC, latSW, lngSW, latNE, lngNE = GEO.get_region_box(args.location)
			region = (lngSW, latSW, lngNE, latNE)
			sys.stdout.write('Google found region at %f,%f and %f,%f\n' % region)
	else:
		region = None
	
	try:
		stream_tweets(api, args.words, region)
	except KeyboardInterrupt:
		sys.stderr.write('\nTerminated by user\n')
				
	GEO.print_stats()