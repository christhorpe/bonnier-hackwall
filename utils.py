import os
import datetime
import yql

from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import models




def render_template(self, end_point, template_values):
	path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
	response = template.render(path, template_values)
	self.response.out.write(response)


def monthname_to_month(monthname):
	if monthname == "Jan":
		month = 1
	if monthname == "Feb":
		month = 2
	if monthname == "Mar":
		month = 3
	if monthname == "Apr":
		month = 4
	if monthname == "May":
		month = 5
	if monthname == "Jun":
		month = 6
	if monthname == "Jul":
		month = 7
	if monthname == "Aug":
		month = 8
	if monthname == "Sep":
		month = 9
	if monthname == "Oct":
		month = 10
	if monthname == "Nov":
		month = 11
	if monthname == "Dec":
		month = 12
	return month


def convert_twitter_datetime(theirdatetime):
	thisdatetime = datetime.datetime(int(theirdatetime[12: 16]), monthname_to_month(theirdatetime[8: 11]), int(theirdatetime[5: 7]), int(theirdatetime[17: 19]), int(theirdatetime[20: 22]), int(theirdatetime[23: 25]))
	return thisdatetime


def get_user_details(user):
	details = memcache.get("t_" + user.name)
	if not details:
		query = "select class, content from html where url = \"http://twitter.com/%s\" and (xpath=\"//div[@id='profile']//span\" or xpath=\"//li[@id='profile_tab']//span\")" % user.name
		y = yql.Public()
		yqlresponse = y.execute(query)
		details = yqlresponse['query']['results']['span']
		memcache.add("t_" + user.uid, details, 1000)
	return details


def get_max_tweet():
	tweet = models.Tweet.all().order('-uid').get()
	if tweet:
		return tweet.uid
	else:
		return "1"



def process_tweet(rawtweet):
	user_name = rawtweet['from_user']
	user_uid = rawtweet['from_user_id']
	user = models.User.get_or_insert("u_" + user_uid, name=user_name, uid=user_uid, tweetlist=[])		
	tweet_uid = rawtweet['id']
	tweet_text = rawtweet['text']
	tweet_created = convert_twitter_datetime(rawtweet['created_at'])
	tweet = models.Tweet.get_or_insert("t_" + tweet_uid, text=tweet_text, uid=tweet_uid, created_at=tweet_created, user=user)	
	if str(tweet.key()) not in user.tweetlist:
		user.tweetcount += 1
		user.tweetlist.append(str(tweet.key()))
		user.put()
	return tweet