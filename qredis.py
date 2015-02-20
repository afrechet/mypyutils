import redis
import json

class Queue(object):
	"""Simple queue with redis backend and json encoding/decoding of items."""

	def __init__(self, name, namespace='queue', **redis_kwargs):
		"""The default connection parameters are: host='localhost', port=6379, db=0"""
		self.__db = redis.StrictRedis(**redis_kwargs)
		name = '%s:%s' %(namespace, name)
		self.key = name

	def qsize(self):
		"""Return the approximate size of the queue."""
		return self.__db.llen(self.key)

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return self.qsize() == 0

	def put(self, item):
		"""Put item into the queue without blocking."""

		value = json.dumps(item)

		self.__db.rpush(self.key, value)

	def get(self, block=True, timeout=None):
		"""Remove and return an item from the queue. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""

		if block:
			value = self.__db.blpop(self.key, timeout=timeout)
			if value != 'nil' and value:
				item = json.loads(value[1])
			else:
				item = None
		else:
			value = self.__db.lpop(self.key)
			if value != 'nil' and value:
				item = json.loads(value)
			else:
				item = None
		return item

class Stack(Queue):
    def get(self,block=True, timeout=None):
		"""Remove and return an item from the stack. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""

		if block:
			value = Queue.__db.brpop(self.key, timeout=timeout)
			if value != 'nil' and value:
				item = json.loads(value[1])
			else:
				item = None
		else:
			value = Queue.__db.rpop(self.key)
			if value != 'nil' and value:
				item = json.loads(value)
			else:
				item = None
		return item

