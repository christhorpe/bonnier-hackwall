#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import yql

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue

import utils
import models


class MainHandler(webapp.RequestHandler):
  def get(self):
	users = models.User.all().order('-tweetcount')
	template_values = {
		"users": users
	}
	utils.render_template(self, "views/home.html", template_values)


class PersonHandler(webapp.RequestHandler):
  def get(self, uid):
	users = models.User.all().order('-tweetcount')
	user = models.User.get_by_key_name("u_" + uid)
	tweets = models.Tweet.get(user.tweetlist)
	details = utils.get_user_details(user)
	template_values = {
		"users": users,
		"user": user,
		"tweets": tweets,
		"details": details
	}
	utils.render_template(self, "views/person.html", template_values)



class LiveHandler(webapp.RequestHandler):
	def get(self, mode):
		tweets = models.Tweet.all().order('-created_at').fetch(10)
		template_values = {
			"tweets": tweets,
			"searchterm": self.request.get("q")
		}
		if mode == "panel":
			utils.render_template(self, "views/panel.html", template_values)
		else:
			utils.render_template(self, "views/live.html", template_values)


class SearchHandler(webapp.RequestHandler):
  def get(self):
	tweets = models.Tweet.all().search(self.request.get("q")).order('-created_at').fetch(1000)
	template_values = {
		"tweets": tweets,
		"searchterm": self.request.get("q")
	}
	utils.render_template(self, "views/search.html", template_values)




class FeedHandler(webapp.RequestHandler):
	def get(self):
		if not self.request.get("page"):
			page = "1"
		else:
			page = self.request.get("page")
		if not self.request.get("since_id"):
			since_id = utils.get_max_tweet()
		else:
			since_id = self.request.get("since_id")
		query = "select * from json where url=\"http://search.twitter.com/search.json?q=%23bonnierhackday&page="+ page +"&since_id="+ since_id +"\""
		self.response.out.write(query)
		self.response.out.write("<br />")
		y = yql.Public()
		yqlresponse = y.execute(query)
		try:
			results = yqlresponse['query']['results']['json']['results']
			if len(results) > 0:
				for rawtweet in results:
					tweet = utils.process_tweet(rawtweet)
					self.response.out.write(tweet.text)
					self.response.out.write("<br />")
				self.response.out.write("more to scrape")
				self.response.out.write("<br />")
				taskqueue.add(url='/scrape/feed', params={"page":str(int(page) + 1), "since_id":since_id}, method='GET')
		except:
			self.response.out.write(yqlresponse)



def main():
	application = webapp.WSGIApplication([
			('/', MainHandler),
			('/search', SearchHandler),
			('/live()', LiveHandler),
			('/live/(panel)', LiveHandler),
			('/person/(.*)', PersonHandler),
			('/scrape/feed', FeedHandler)
	], debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
