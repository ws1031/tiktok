import redis
from logger import logger
from config import *
import re
import time

class RedisClient(object):
	def __init__(self):
		self.db1 = redis.StrictRedis(host=RHOST, port=RPORT, db=1, password=RPASSWORD, decode_responses= True)
		self.db2 = redis.StrictRedis(host=RHOST2, port=RPORT2, db=1, password=RPASSWORD2, decode_responses= True)
		self.db3 = redis.StrictRedis(host=RHOST2, port=RPORT2, db=2, password=RPASSWORD2, decode_responses= True)
		self.key1 = 'users' #所积累的sec_user_id，最重要的原始数据
		self.key2 = 'awemes' #短视频，get_clips需要的
		self.key3 = 'rooms' #直播间id，获取直播间数据的
		self.key4 = 'item_lists' #直播间id和用户sec_user_id，获取商品信息的
		self.key5 = 'params' #参数，比如抖音的cookie
		self.key6 = 'feigua_aweme_id' #飞瓜获取来的的短视频id，是sec_user_id的来源之一
		self.key7 = 'following' #用户的关注信息，用来获取pre_users的
		self.key8 = 'pre_users' #pre_users在确认带货之后变成正式users，是sec_user_id的另一来源
		self.key9 = 'live_users'
		self.key10 = 'items'
		#self.id = ID

	def add_params(self, name, value):
		try:
			self.db2.hset(self.key5, name, value)
		except TypeError as e:
			logger.error('添加params失败-param-' + name + '-' + value)

	def get_params(self, name):
		for i in range(100):
			try:
				return self.db2.hget(self.key5, name)
			except TypeError as e:
				logger.error('获取params失败-param-' + name)

	def is_user(self, sec_user_id):
		return self.db1.zrank(self.key1, sec_user_id) #是否已经在user表中了
	
	def add_users(self, sec_user_id):
		score = int(self.db1.zrange(self.key1, 0, 0, withscores=True)[0][1]) #以最低分数作为分数
		self.db1.zadd(self.key1, {sec_user_id: score})

	def get_users(self):
		return self.db1.zrange(self.key1, 0, 50000) #每次返回分数最低的10000个

	def increase_user_score(self, user):
		self.db1.zincrby(self.key1, 1, user)

	def delete_users(self, sec_user_id):
		self.db1.zrem(self.key1, sec_user_id)

	def add_live_users(self, sec_user_id, status):
		try:
			self.db1.zadd(self.key9, {sec_user_id: status})
		except TypeError as e:
			logger.error('添加live_user失败-sec_user_id-' + sec_user_id)

	def get_live_users(self, status_a, status_b):
		for i in range(100):
			try:
				return self.db1.zrangebyscore(self.key9, status_a, status_b)
			except TypeError as e:
				logger.error('获取live_users失败')
		return []

	def delete_live_users(self, sec_user_id):
		try:
			self.db1.zrem(self.key9, sec_user_id)
		except TypeError as e:
			logger.error('删除live_user失败-sec_user_id-' + sec_user_id)

	def is_live_user(self, sec_user_id):
		return self.db1.zrank(self.key9, sec_user_id) #是否已经在live_user表中了

	def add_rooms(self, room_id):
		try:
			self.db1.sadd(self.key3, room_id)
		except TypeError as e:
			logger.error('添加room失败-room_id-' + room_id)

	def get_rooms(self):
		for i in range(100):
			try:
				return list(self.db1.smembers(self.key3))
			except TypeError as e:
				logger.error('获取rooms失败')
		return []

	def delete_rooms(self, room_id):
		try:
			self.db1.srem(self.key3, room_id)
		except TypeError as e:
			logger.error('删除room失败-room_id-' + room_id)

	def add_item_lists(self, room_sec_id): 
		try:
			self.db1.sadd(self.key4, room_sec_id)
		except TypeError as e:
			logger.error('添加item_list失败-room_id-' + room_sec_id)

	def get_item_lists(self):
		for i in range(100):
			try:
				return list(self.db1.smembers(self.key4))
			except TypeError as e:
				logger.error('获取item_lists失败')

	def delete_item_lists(self, room_sec_id):
		try:
			self.db1.srem(self.key4, room_sec_id)
		except TypeError as e:
			logger.error('删除item_list失败-room_id-' + room_sec_id)

	def add_items(self, item_list):
		for i in range(100):
			try:
				self.db1.sadd(self.key10, *item_list)
				break
			except TypeError as e:
				logger.error('添加item_list失败')

	def get_items(self):
		for i in range(100):
			try:
				return list(self.db1.smembers(self.key10))
			except TypeError as e:
				logger.error('获取items失败')

	def delete_items(self, item):
		try:
			self.db1.srem(self.key10, item)
		except TypeError as e:
			logger.error('删除item失败-item-' + item)

	def add_awemes(self, aweme_id):
		try:
			self.db1.sadd(self.key2, aweme_id)
		except TypeError as e:
			logger.error('添加aweme失败-awme_id-' + aweme_id)

	def get_awemes(self):
		for i in range(100):
			try:
				return list(self.db1.smembers(self.key2))
			except TypeError as e:
				logger.error('获取awemes失败')
		return []

	def delete_awemes(self, aweme):
		try:
			self.db1.srem(self.key2, aweme)
		except TypeError as e:
			logger.error('删除aweme失败-aweme_id-' + aweme)

	def get_feigua_awemes(self):
		return list(self.db3.smembers(self.key6))

	def delete_feigua_awemes(self, aweme):
		self.db3.srem(self.key6, aweme)

	def add_following(self, following): #用户的following
		self.db3.rpush(self.key7, following)

	def get_following(self): 
		return self.db3.lpop(self.key7)

	def count_following(self):
		return self.db3.llen(self.key7)

	def add_pre_users(self, sec_user_id):
		self.db3.rpush(self.key8, sec_user_id)

	def get_pre_users(self):
		return self.db3.lpop(self.key8)

	def count_pre_users(self):
		return self.db3.llen(self.key8)

if __name__ == '__main__':
	redis_client = RedisClient()
	redis_client.reset_live_users()
	#redis_client.add_params('dy_cookie', 'install_id=2172274732445896; ttreq=1$596ed4a4d3cc39fbf271b936a59a706c65f565d4; odin_tt=c2cb2a0f3d8275c392edebf0454dbdad5e546e022695aed1a9eabf0753c18735dff1d2c8a549c4f6c43531402e03e058956e8eaab3689f72b6b97c6f4b5713cb')
	#print(redis_client.get_following())

"""

"""