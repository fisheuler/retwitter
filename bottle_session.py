# session management


import random

import pickle

import settings


r = settings.r


_sidChars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

_defaultTimeout=30*60

_defaultCookieName='gsid'


class Session(dict):

	def __init__(self,request,response,name=_defaultCookieName,timeout=_defaultTimeout):
		"""
		request response --- parent's handler
		name --- cookie name
		timeout --- session's keep time

		"""

		self.request = request
		self.response = response
		self._timeout = timeout
		self._name = name
		self._new = True
		self._invalid = False
		dict.__init__(self)


		_name = request.COOKIES.get(self._name,None)
		
		if _name:
			self._sid = _name
			data = r.get(self._sid)

			if data:
				self.update(pickle.loads(data))
				
				r.set(self._sid,data)
				r.expire(self._name,self._timeout)
				self._new = False
				
				return 

		# create a new session ID

		self._sid = random.choice(_sidChars)+random.choice(_sidChars)+\
				random.choice(_sidChars)+random.choice(_sidChars)+\
				random.choice(_sidChars)+random.choice(_sidChars)+\
				random.choice(_sidChars)+random.choice(_sidChars)

		self.response.set_cookie(self._name,self._sid,path='/')
	
	def save(self):
		if not self._invalid:
			r.set(self._sid,pickle.dumps(self.copy()))
			r.expire(self._name,self._timeout)
	
	def is_new(self):
		return self._new
	
	def invalidate(self):
		self.response.set_cookie(self._name,'',expires=-100)
		r.delete(self._sid)
		self.clear()
		self._invalid=True




