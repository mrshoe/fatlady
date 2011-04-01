import datetime
import pprint
from bottle import route, run, template
import json
import urllib2

pp = pprint.PrettyPrinter(indent=4)
listed_sports = {
	'mlb' : 'MLB Baseball',
	'nba' : 'NBA Basketball',
	'ncb' : 'NCAA Basketball',
	'ncf' : 'NCAA Football',
	'nfl' : 'NFL Football',
	'nhl' : 'NHL Hockey',
}

class Game(object):
	def __init__(self, sport, game):
		self.sport = sport
		self.home = game['home']['name']
		self.away = game['away']['name']
		if game['status'] == 1:
			self.status = game['statusText']
		elif game['status'] == 2:
			self.status = 'In Progress'
		elif game['status'] == 3:
			self.status = 'Game Over'
		else:
			self.status = 'In Progress'

def is_in_range(game):
	# delta is 5 hours for timezone adjustment + we care about 12 hours in either direction
	mintime = datetime.datetime.now() - datetime.timedelta(hours=17)
	maxtime = datetime.datetime.now() + datetime.timedelta(hours=7)
	gametime = datetime.datetime.strptime(game['date'], '%Y%m%d%H%M%S')
	return gametime > mintime and gametime < maxtime

@route('/')
def all_games():
	espndata = urllib2.urlopen('http://espn.go.com/aggregator/cached/tea/feed')
	result = json.loads(espndata.read())
	#pp.pprint(result)
	sports = []
	for sport in result['sports']:
		s = sport['sport']
		if s in listed_sports:
			league = sport['leagues'][0]
			sports.append((listed_sports[s], [Game(s, g) for g in league['games'] if is_in_range(g)]))
	return template('allgames.tmpl', sports=sports)

run(host='0.0.0.0', port=8888, reloader=True)
