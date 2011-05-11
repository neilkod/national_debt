#/usr/bin/python
import urllib2, ConfigParser, time
import tweepy
from BeautifulSoup import BeautifulSoup

TWITTER_ACCOUNT = 'usadebtlevel'
CONFIGURATION_FILE = 'config.cfg'
DATAFILE = 'data/national_debt.tsv'

# tweets to @usadebtlevel

""" requires a config file in this format
[twitteraccount]
CONSUMER_KEY = xxxxxxxxxxxxx
CONSUMER_SECRET = yyyyyyyyyyyyyyyyyyyyyyyyyy
ACCESS_KEY = zzzzzzzzzzzzzzzzzzzzzzzzzz
ACCESS_SECRET = bbbbbbbbbbbbbbbbbbbbbbbbbb
"""

def log_national_debt(datafile, as_of, debt, population):
	""" logs the date, debt, and population to DATAFILE"""
	
	#reformat the date from mm/dd/yy to yyyymmdd
	dt = time.strptime(as_of, '%m/%d/%Y')
	dt_string = time.strftime('%Y%m%d', dt)
	
	file_handle = open(datafile, 'a')
	log_item = '%s\t%d\t%d' % (dt_string, debt, population)
	file_handle.write(log_item + '\n')
	file_handle.close()

def tweet_national_debt(twitter_config, tweet_string):
	""" given the twitter config and the tweet itself, create a
	    twitter session and send the tweet."""
	
	auth = tweepy.OAuthHandler(twitter_config['CONSUMER_KEY'], \
		twitter_config['CONSUMER_SECRET'])

	auth.set_access_token(twitter_config['ACCESS_KEY'], \
		twitter_config['ACCESS_SECRET'])

	api = tweepy.API(auth)
	api.update_status(tweet_string)

def get_twitter_config(config_file, twitter_account):
	config = ConfigParser.RawConfigParser()
	config.read(config_file)
	return dict(config.items(twitter_account))

def get_us_population():
	""" retrieves the population from census.gov """
	population_url = 'http://www.census.gov/main/www/popclock.html'
	population_page = urllib2.urlopen(population_url)
	soup = BeautifulSoup(population_page)
	population = soup.find('span',{'id':'usclocknum'}).text
	return population

def get_national_debt():
	"""gets the current national debt from treasurydirect.gov"""
	debt_url = 'http://www.treasurydirect.gov/NP/BPDLogin?application=np'
	page = urllib2.urlopen(debt_url)
	soup = BeautifulSoup(page)
	
	# ugly BeautifulSoup code to get the debt and the updated(as_of) date
	debt = soup.find('table',{'class':'data1'}).findAll('td')[3].text
	as_of = soup.find('table',{'class':'data1'}).findAll('td')[0].text
	return debt, as_of

def main():
	twitter_config = get_twitter_config(CONFIGURATION_FILE, TWITTER_ACCOUNT)
	population = get_us_population()
	national_debt, as_of = get_national_debt()

	# create numeric representations of the debt and the amount
	# used for division
	
	debt_amount = float(national_debt.replace(',',''))
	population_amount = int(population.replace(',',''))
	per_person_amount = debt_amount / population_amount

	tweet_string = "US National debt as of %s is $%s, or $%.2f for each person(%s) in the US" \
		% (as_of, national_debt,per_person_amount,population)
	
	log_national_debt(DATAFILE, as_of, debt_amount, population_amount)

	print tweet_string
	tweet_national_debt(twitter_config, tweet_string)

if __name__ == '__main__':
	main()


