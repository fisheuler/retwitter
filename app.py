#!/usr/bin/env python


import bottle
import redis
import settings
import hashlib

settings.r = redis.Redis(host=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB)

from bottle_session import Session
from model import User,Post,Timeline

reserved_usernames = 'follow mentions home signup login logout post'


def authenticate(func):
	def auth(*args,**kwargs):
		session = Session(bottle.request,bottle.response)
		if not session.is_new():
			user = User.find_by_id(session['id'])
			if user:
				return func(user,*args,**kwargs)
		bottle.redirect('/login')
	return auth



def logged_in_user():
	session = Session(bottle.request,bottle.response)
	if not session.is_new():
		return User.find_by_id(session['id'])
	return None


def user_is_logged():
	if logged_in_user():
		return True
	return False


@bottle.route('/')
def index():
	if user_is_logged():
		bottle.redirect('/home')
	return bottle.template('home_not_logged',logged=False)


@bottle.route('/home')
@authenticate
def home(user):
	bottle.TEMPLATES.clear()
	counts = user.followees_count,user.followers_count,user.tweet_count

	if len(user.posts()) > 0:
		last_tweet = user.posts()[0]
	else:
		last_tweet = None
	return bottle.template('timeline',timeline=user.timeline(),page="timeline",username = user.username,counts=counts,last_tweet = last_tweet,logged=True)


@bottle.route('/mentions')
@authenticate
def mentions(user):
	counts= user.followees_count,user.followers_count,user.tweet_count
	return bottle.template("mentions",mentions=user.mentions(),page="mentions",username=user.username,counts=counts,posts=user.post()[:1],logged=True)

@bottle.route('/:name')
def user_page(name):
	is_following,is_logged= False,user_is_logged()
	user= User.find_by_username(name)
	if user:
		counts = user.followees_count,user.followers_count,user.tweet_count
		logged_user= logged_in_user()
		himself = logged_user.username == name
		if logged_user:
			is_following = logged_user.following(user)
		
		return bottle.template('user',posts=user.posts(),counts=counts,page='user',username=user.username,logged=is_logged,is_following=is_following,himself=himself)
	else:
		return bottle.HTTPError(code=404)



@bottle.route('/:name/following')
@authenticate
def following(name):
	user = User.find_by_username(name)
	is_logged=user_is_logged()

	if user:
		return bottle.template('following',followees= user.followees,page="followee",logged=is_logged)
	
	return bottle.HTTPError(code=404)
	
@bottle.route('/:name/followers')
@authenticate
def followers(name):
	user = User.find_by_username(name)
	is_logged = user_is_logged()
	if user:
		return bottle.template('followers',followers=user.followers,page="followers",logged=is_logged)
	return bottle.HTTPError(code=404)


@bottle.route('/:name/statuses/:id')
@bottle.validate(id=int)
def status(name,id):
	post = Post.find_by_id(id)
	if post:
		if post.user.username == name:
			return bottle.template('single',username=post.user.username,tweet=post,page='single',logged=user_is_logged())

	return bottle.HTTPError(code=404,message='tweet not found')


@bottle.route('/post',method='POST')
@authenticate
def post(user):
	content = bottle.request.POST['content']
	Post.create(user,content)
	bottle.redirect('/home')

@bottle.route('/follow/:name',method='POST')
@authenticate
def followpost(user,name):
	user_to_follow = User.find_by_username(name)
	if user_to_follow:
		user.follow(user_to_follow)
	bottle.redirect('/%s' % name)

@bottle.route('/unfollow/:name',method='POST')
@authenticate
def unfollowpost(user,name):
	user_to_unfollow = User.find_by_username(name)
	if user_to_unfollow:
		user.stop_following(user_to_unfollow)
	bottle.redirect('/%s' % name)

@bottle.route('/signup')
@bottle.route('/login')
def login():
	bottle.TEMPLATES.clear()
	if user_is_logged():
		bottle.redirect('/home')
	return bottle.template('login',page='login',error_login=False,error_signup=False,logged=False)

@bottle.route('/login',method='POST')
def login():
	if 'name' in bottle.request.POST and 'password' in bottle.request.POST:
		name = bottle.request.POST['name']
		password = bottle.request.POST['password']
		
		user=User.find_by_username(name)
		
		if user and user.password == hashlib.md5(settings.SALT+password).hexdigest():
			sess = Session(bottle.request,bottle.response)
			sess['id']=user.id
			sess.save()
			bottle.redirect('/home')
	return bottle.template('login',page='login',error_login=True,error_signup=False,logged=False)


@bottle.route('/logout')
def logout():
	sess = Session(bottle.request,bottle.response)
	sess.invalidate()
	bottle.redirect('/')

@bottle.route('/signup',method='POST')
def sign_up():
	if 'name' in bottle.request.POST and 'password' in bottle.request.POST:
		name= bottle.request.POST['name']
		if name not in reserved_usernames.split():
			password = bottle.request.POST['password']
			user = User.create(name,password)
			if user:
				sess = Session(bottle.request,bottle.response)
				sess['id'] = user.id
				sess.save()
				bottle.redirect('/home')
	return bottle.template('login',page='login',error_login=False,error_signup=True,logged=False)

@bottle.route('/static/:filename')
def static_file(filename):
	bottle.send_file(filename,root='static/')

bottle.debug(True)
bottle.run(host='localhost',port=9746,reloader=True)





