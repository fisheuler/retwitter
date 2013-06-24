#!/usr/bin/env python

import redis
import re
import settings
import hashlib

r = settings.r


class Timeline:
	def page(self,page):
		pageStart = (page-1)*10
		pageEnd   = (page)*10
		return [Post(post_id) for post_id in r.lrange('timeline',pageStart,pageEnd)]

class Model(object):
	def __init__(self,id):
		self.__dict__['id'] = id

	def __eq__(self,other):
		return self.id == other.id

	def __setattr__(self,name,value):
		if name not in self.__dict__:
			modelName = self.__class__.__name__.lower()
			key = '%s:id:%s:%s' % (modelName,self.id,name.lower())
			r.set(key,value)
		else:
			self.__dict__[name] = value

	def __getattr__(self,name):
		if name not in self.__dict__:
			modelName = self.__class__.__name__.lower()
			value = r.get('%s:id:%s:%s' % (modelName,self.id,name.lower()))
			if value:
				return value
			raise AttributeError(' cannot find %s ' % name)
		else:
			return object.__getattribute__(self,name)

class User(Model):
	@staticmethod
	def find_by_username(username):
		userId = r.get("user:username:%s" % username)
		if userId is not None:
			return User(int(userId))
		else:
			return None
	
	@staticmethod
	def find_by_id(userId):
		if r.exists("user:id:%s:username" % userId):
			return User(int(userId))
		else:
			return None

	@staticmethod
	def create(username,password):
		userId = r.incr("user:uid")
		if not r.get("user:username:%s" % username):
			r.set("user:id:%s:username" % userId,username)
			r.set("user:username:%s" % username,userId)

			salt = settings.SALT
			encryptPassword = hashlib.md5(salt+password).hexdigest()
			r.set("user:id:%s:password" % userId,encryptPassword)			
			r.lpush("users",userId)
			return User(userId)
		return None

	def posts(self,page=1):
		pageStart,pageEnd = (page-1)*10,page*10

		posts = r.lrange("user:id:%s:posts" % self.id,pageStart,pageEnd)
		if posts:
			return [Post(int(postId)) for postId in posts]
		return []

	
	def timeline(self,page=1):
		pageStart,pageEnd = (page-1)*10,page*10
		timeline = r.lrange("user:id:%s:timeline" % self.id,pageStart,pageEnd)
		if timeline:
			return [Post(int(postId)) for postId in timeline]

		return []

	def mentions(self,page=1):
		pageStart,pageEnd = (page-1)*10,page*10
		mentions = r.lrange("user:id:%s:mentions" % self.id,pageStart,pageEnd)
		if mentions:
			return [Post(int(postId)) for postId in mentions]
		return []

	def add_post(self,post):
		r.lpush("user:id:%s:posts" % self.id, post.id)
		r.lpush("user:id:%s:timeline" % self.id,post.id)
		r.sadd('posts:id',post.id)

	def add_timeline_post(self,post):
		r.lpush("user:id:%s:timeline" % self.id,post.id)

	def add_mention(self,post):
		r.lpush("user:id:%s:mentions" % self.id,post.id)

	def follow(self,user):
		if user == self:
			return
		else:
			r.sadd("user:id:%s:followees" % self.id,user.id)
			user.add_follower(self)
	
	def unfollow(self,user):
		r.srem("user:id:%s:followees" % self.id,user.id)
		user.remove_follower(self)
	
	def following(self,user):
		if r.sismember("user:id:%s:followees" % self.id,user.id):
			return True
		return False

	
	@property
	def followers(self):
		followers = r.smembers("user:id:%s:followers" % self.id)
		if followers:
			return [User(int(userId)) for userId in followers]
		return []


	@property
	def followees(self):
		followees = r.smembers("user:id:%s:followees" % self.id)
		if followees:
			return [User(int(userId)) for userId in followees]
		return []

	@property
	def tweet_count(self):
		return r.llen("user:id:%s:posts" % self.id) or 0

	@property
	def followees_count(self):
		return r.scard("user:id:%s:followees" % self.id) or 0
	
	@property
	def followers_count(self):
		return r.scard("user:id:%s:followers" % self.id) or 0

	
	def add_follower(self,user):
		r.sadd("user:id:%s:followers" % self.id, user.id)

	def remove_follower(self,user):
		r.srem("user:id:%s:followers" % self.id, user.id)



class Post(Model):
	
	@staticmethod
	def create(user,content):
		postId = r.incr("post:uid")
		post = Post(postId)
		post.content = content
		post.user_id = user.id

		user.add_post(post)
	
		r.lpush("timeline",postId)
	
		for follower in user.followers:
			follower.add_timeline_post(post)


		mentions = re.findall('@\w+',content)
		
		for mention in mentions:
			u = User.find_by_username(mention[1:])
			if u:
				u.add_mention(post)
	@staticmethod
	def find_by_id(id):
		if r.sismember('posts:id',int(id)):
			return Post(id)
		return None


	@property
	def user(self):
		return User.find_by_id(r.get("post:id:%s:user_id" % self.id))


def main():
	pass

if __name__ == '__main__':
	main()
			
		
	



	
		

