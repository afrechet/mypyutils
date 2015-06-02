import redis

import random

import json
import zlib

import mmh3

class _Structure(object):
	"""
	Simple limited access data structure with redis backend. 
	This means the items will be stored as strings, so there can be some
	confusion when loading back an item from redis (e.g. the string representation
	of the character '0' and the integer 0 are the same).
	"""

	def __init__(self, name, namespace, **redis_kwargs):
		"""Create a structure.

		name - the structure's name, used to identify its key in redis.
		namespace - the stucture's namespace, usually to identify the 
			class of structure (e.g. queue, stack, ...)
		redis_kwargs - the redis arguments to create a redis connection.
			Important defaults are host='localhost', port=6379, password=None.
		"""
		self.db = redis.StrictRedis(**redis_kwargs)

		#Check if the db is alive.
		self.db.ping()

		key = '%s:%s' %(namespace, name)

		self.key = key

	def size(self):
		"""Return the approximate size of the queue."""
		return self.db.llen(self.key)

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return self.size() == 0

	def put(self, item):
		"""Put item into the queue without blocking."""
		self.db.rpush(self.key, item)

	def get(self, block=True, timeout=None):
		raise NotImplementedException('Abstract class _Structure does not implement get.')

class Queue(_Structure):
	"""
	Implements structure that gets the opposite side it puts.
	"""
	__index = 0

	def __init__(self, name = None, namespace='queue', **redis_kwargs):
		"""The default connection parameters are: host='localhost', port=6379, db=0"""

		if name == None:
			name = 'default%d' % Queue.__index
			Queue.__index+=1

		_Structure.__init__(self,name,namespace,**redis_kwargs)

	def get(self, block=True, timeout=None):
		"""Remove and return an item from the queue. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""

		if block:
			item = self.db.blpop(self.key, timeout=timeout)
			if item != 'nil' and item:
				item = item[1]
			else:
				item = None
		else:
			item = self.db.lpop(self.key)
			if item != 'nil' and item:
				item = item
			else:
				item = None
		return item

class Stack(_Structure):
	"""
	Implements structure that gets the same side it puts.
	"""
	__index = 0

	def __init__(self, name = None, namespace='stack', **redis_kwargs):
		"""The default connection parameters are: host='localhost', port=6379, db=0"""

		if name == None:
			name = 'default%d' % Stack.__index
			Stack.__index+=1

		_Structure.__init__(self,name,namespace,**redis_kwargs)

	def get(self, block=True, timeout=None):
		"""Remove and return an item from the stack. 

		If optional args block is true and timeout is None (the default), block
		if necessary until an item is available."""

		if block:
			item = self.db.brpop(self.key, timeout=timeout)
			if item != 'nil' and item:
				item = item[1]
			else:
				item = None
		else:
			item = self.db.rpop(self.key)
			if item != 'nil' and item:
				item = item
			else:
				item = None

		return item

class EncoderDecorator(_Structure):
	"""
	Structure decorator that encodes/decodes entries in some provided way.
	"""

	def __init__(self, structure, encoder):
		"""
		structure - data structure to decorate.
		encoder - encoder object that encodes/decodes entries to and from the redis structure.
			Must have an encode(item) and a decode(item) method which encode an item to the queue and
			decodes an item from the queue, respectively. See @JSONEncoder and @ZlibEncoder.
		"""
		self.__structure = structure
		self.__encoder = encoder

	def size(self):
		return self.__structure.size()

	def empty(self):
		return self.__structure.empty()

	def put(self, item):
		try:
			encodeditem = self.__encoder.encode(item)
		except Exception, e:
			raise Exception('Could not encode item "'+str(item)+'" with provided encoder.',e)
		self.__structure.put(encodeditem)

	def get(self, block=True, timeout=None):
		encodeditem = self.__structure.get(block,timeout)
		
		if encodeditem == None:
			return encodeditem

		try:
			decodeditem = self.__encoder.decode(encodeditem)
		except Exception, e:
			raise Exception('Could not decode item "'+str(encodeditem)+'" with provided encoder.',e)
		return decodeditem

class JSONEncoder(object):
	"""
	JSON encoder to use with encoder decorator.
	""" 
	def __init___(self):
		return
	def encode(self,item):
		return json.dumps(item)
	def decode(self,item):
		return json.loads(item)

class ZlibEncoder(object):
	"""
	zlib compressor to use with encoder decorator.
	"""
	def __init___(self):
		return
	def encode(self,item):
		return zlib.compress(str(item))
	def decode(self,item):
		return eval(zlib.decompress(item))


class MultiStruct(_Structure):
	"""Use multiple structures through a single structure, load balancing with a hash function."""

	def __init__(self,structures,hashf=None,preserve=False):		
		"""
		structures - list of structure to use (size at least 2).
		hashf - hash function to use for load balancing. 
			If 'None', default 32-bits Murmur hash mod number of structures is used.
		preserve - whether to preserve the structures' properties. If 'True', then
			all the provided structures must be of the same type, one of the provided
			structure will be set aside and used to honor 'put'/'get' order (so there must
			be at least 3 structures). If 'False', then 'get' returns item a random structure.
		"""
		self.__opstruct = None
		if preserve:
			t = None
			for structure in structures:
				if t == None:
					t = type(structure).__name__
				else:
					if t != type(structure).__name__:
						raise ValueError('Provided two different types of structures ("%s" and "%s") to MultiStruct composer.' % (t,type(structure).__name__))
			if t == None:
				raise ValueError('Provided structure of type "None" to MultiStruct composer.')

			assert len(structures) > 2, 'Must provide at least 3 structures to a property preserving MultiStruct composer.'

			self.__opstruct = structures[0]
			self.__structures = structures[1:]
		else:
			
			assert len(structures) > 1, 'Must provide at least 2 structures to a MultiStruct composer.'
			self.__structures = structures

		if hashf == None:
			self.__hashf = lambda i : mmh3.hash(i)
		else:
			self.__hashf = hashf


	def size(self):
		s = 0
		for structure in self.__structures:
			s += structure.size()
		return s

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return self.size() == 0

	def put(self, item):
		"""Put item into the queue without blocking."""
		h = self.__hashf(str(item))
		i = h % len(self.__structures)
		assert i >= 0 and i < len(self.__structures), 'Calculated index "%s" from hash "%s" for item "%s" is not a proper index into %d structures' % (str(i),h,item,len(self.__structures))

		structure = self.__structures[i]

		if self.__opstruct != None:
			self.__opstruct.put(i)

		structure.put(item)

	def get(self, block=True, timeout=None):
		if self.__opstruct != None:
			i = int(self.__opstruct.get(block,timeout))
			assert i >= 0 and i < len(self.__structures), 'Index "%s" obtained from operations structure is not a proper index into %d structures' % (str(i),len(self.__structures))
			structure = self.__structures[i]
		else:
			structure = random.choice(self.__structures)
		return structure.get(block,timeout)


items = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
items = [str(i) for i in range(10000)]

def testQueue():
	Q = Queue()

	assert Q.empty(), 'Fresh queue is not empty.'
	assert Q.size() == 0, 'Fresh queue does not have size 0.'

	for item in items:
		Q.put(item)

	qsize = Q.size()
	assert qsize == len(items), 'Got queue size %d, expected %d.' % (qsize,len(items))

	size = qsize
	for item in items:
	
		qitem = Q.get()
		size-= 1
		
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)
		
		qsize = Q.size()
		assert qsize == size, 'Got queue size %d, expected %d.' % (qsize,size)

	assert Q.empty(), 'Queue not empty after removing all items.'

	n = 10
	item = items[0]
	for i in range(n):
		Q.put(item)

	qsize = Q.size()
	assert qsize == n, 'Queue with %d duplicate items has size.' % (n,qsize)

	for i in range(n):
		qitem = Q.get(item)
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)

	assert Q.empty(), 'Empty queue is not empty.'
	assert Q.size() == 0, 'Empty queue does not have size 0.'

def testStack():
	S = Stack()

	assert S.empty(), 'Fresh queue is not empty.'
	assert S.size() == 0, 'Fresh queue does not have size 0.'

	for item in items:
		S.put(item)

	qsize = S.size()
	assert qsize == len(items), 'Got queue size %d, expected %d.' % (qsize,len(items))

	size = qsize
	for item in reversed(items):
	
		qitem = S.get()
		size-= 1
		
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)
		
		qsize = S.size()
		assert qsize == size, 'Got queue size %d, expected %d.' % (qsize,size)

	assert S.empty(), 'Queue not empty after removing all items.'

	n = 10
	item = items[0]
	for i in range(n):
		S.put(item)

	qsize = S.size()
	assert qsize == n, 'Queue with %d duplicate items has size.' % (n,qsize)

	for i in range(n):
		qitem = S.get(item)
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)

	assert S.empty(), 'Empty queue is not empty.'
	assert S.size() == 0, 'Empty queue does not have size 0.'


def testMultiStruct():
	Qnum = 5
	Qs = [Queue() for num in range(Qnum)]

	Q = MultiStruct(Qs,preserve = True)

	assert Q.empty(), 'Fresh queue is not empty.'
	assert Q.size() == 0, 'Fresh queue does not have size 0.'

	for item in items:
		Q.put(item)

	qsize = Q.size()
	assert qsize == len(items), 'Got queue size %d, expected %d.' % (qsize,len(items))

	size = qsize
	for item in items:
	
		qitem = Q.get()
		size-= 1
		
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)
		
		qsize = Q.size()
		assert qsize == size, 'Got queue size %d, expected %d.' % (qsize,size)

	assert Q.empty(), 'Queue not empty after removing all items.'

	n = 10
	item = items[0]
	for i in range(n):
		Q.put(item)

	qsize = Q.size()
	assert qsize == n, 'Queue with %d duplicate items has size.' % (n,qsize)

	for i in range(n):
		qitem = Q.get(item)
		assert qitem == item, 'Got item "%s", expected "%s".' % (qitem,item)

	assert Q.empty(), 'Empty queue is not empty.'
	assert Q.size() == 0, 'Empty queue does not have size 0.'	




if __name__ == '__main__':

	integers = [str(i) for i in range(1000)]

	S = 10
	Qs = [Queue() for s in range(S)]

	Q = MultiStruct(Qs,preserve = True)

	for item in integers:
		Q.put(item)

	for q in Qs:
		print q.size()



