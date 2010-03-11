from google.appengine.ext import db
from google.appengine.ext import search


class User(db.Model):
	name = db.StringProperty()
	uid = db.StringProperty()
	tweetcount = db.IntegerProperty(default=0)
	tweetlist = db.StringListProperty()
	participant = db.BooleanProperty(default=False)


class Tweet(search.SearchableModel):
	text = db.TextProperty()
	uid = db.StringProperty()
	created_at = db.DateTimeProperty()
	user = db.ReferenceProperty(User)

	