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
		self.key2 = 'awemes' #短视频，好像不需要了
		self.key3 = 'rooms' #直播间id，获取直播间数据的
		self.key4 = 'item_lists' #直播间id和用户sec_user_id，获取商品信息的
		self.key5 = 'params' #参数，比如抖音的cookie
		self.key6 = 'feigua_aweme_id' #飞瓜获取来的的短视频id，是sec_user_id的来源之一
		self.key7 = 'following' #用户的关注信息，用来获取pre_users的
		self.key8 = 'pre_users' #pre_users在确认带货之后变成正式users，是sec_user_id的另一来源
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

	def add_users(self, sec_user_id, status):
		try:
			self.db1.zadd(self.key1, {sec_user_id: status})
		except TypeError as e:
			logger.error('添加user失败-sec_user_id-' + sec_user_id)

	def get_users(self, status_a, status_b):
		for i in range(100):
			try:
				return self.db1.zrangebyscore(self.key1, status_a, status_b)
			except TypeError as e:
				logger.error('获取users失败')
		return []

	def delete_users(self, sec_user_id):
		try:
			self.db1.zrem(self.key1, sec_user_id)
		except TypeError as e:
			logger.error('删除user失败-sec_user_id-' + sec_user_id)

	def reset_user_status(self):
		try:
			users = self.get_users(1, 1)
			for user in users:
				self.add_users(user, 0)
		except TypeError as e:
			logger.error('重置users失败')

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

	def get_feigua_awemes(self):
		return list(self.db3.smembers(self.key6))

	def delete_feigua_awemes(self, aweme):
		self.db3.srem(self.key6, aweme)

	def add_following(self, following): #用户的following
		self.db3.rpush(self.key7, following)

	def get_following(self): 
		return self.db3.lpop(self.key7)

	def add_pre_users(self, pre_user, status):
		self.db3.zadd(self.key8, {pre_user: status})

	def get_pre_users(self, status_a, status_b):
		return self.db3.zrangebyscore(self.key8, status_a, status_b)

	def delete_pre_users(self, sec_user_id):
		self.db3.zrem(self.key8, sec_user_id)


if __name__ == '__main__':
	redis_client = RedisClient()
	#redis_client.add_params('dy_cookie', 'install_id=111280011708; ttreq=1$155f70f34017463054b07a1ddeab852ca3c3243b; odin_tt=5455854fecdb80efe8fe292bbdbcdb3116c045cda77792677708ba27aa353d44c895ea5667734d919036b345d2ff12ae2c73f582f4e35058e8f9ff7a75b8fe1b')
	print(redis_client.get_following())

"""
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
"""