#通过获取用户following种的其他用户，积累sec_user_id

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import sys
import os
import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import STUPID_KEY_WORDS

class GetPreUsers():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.batch_size = 10
		self.pre_user_list = []
		self.stupid_key_words = STUPID_KEY_WORDS

	def count_following(self):
		return self.redis_client.count_following()

	def count_pre_users(self):
		return self.redis_client.count_pre_users()

	def get_following(self):
		batch = []
		for i in range(self.batch_size):
			batch.append(self.redis_client.get_following())
		return batch

	def add_following_and_pre_users(self):
		for pre_user in self.pre_user_list:
			if self.count_following() < 100000:
				self.redis_client.add_following(pre_user)
			if self.count_pre_users() < 500000:
				self.redis_client.add_pre_users(pre_user)

	def is_qualified_user(self, user):
		if user.get('is_gov_media_vip'):
			return False
		if user.get('enterprise_verify_reason'):
			return False
		if user.get('custom_verify'):
			if not '自媒体' in user.get('custom_verify'):
				if not '主播' in user.get('custom_verify'):
					if not '视频' in user.get('custom_verify'):
						return False
		nickname = user.get('nickname')
		for word in self.stupid_key_words:
			if word in nickname:
				return False
		return True

	def get_pre_users(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_following(sec_user_id)
		except Exception as e:
			logger.error('get_pre_user出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		if not raw_data.get('status_code') == 2096:
			following_list = raw_data.get('followings')
			if len(following_list) == 0:
				logger.error('获取不到数据了，程序退出')
				#sys.exit()
			for user in following_list:
				if self.is_qualified_user(user):
					self.pre_user_list.append(user.get('sec_uid'))
		else:
			logger.info('关注不可见-sec_user_id-' + sec_user_id)

	def run(self):
		if self.count_following() < 100000 or self.count_pre_users() < 500000:
			batch = self.get_following()
			tasks = [gevent.spawn(self.get_pre_users, sec_user_id) for sec_user_id in batch]
			gevent.joinall(tasks)
			logger.info('获取到pre_user-' + str(len(self.pre_user_list)))
			self.add_following_and_pre_users()
			self.pre_user_list.clear()
		else:
			logger.info('已经有太多following或pre_users了')

if __name__ == '__main__':
	get_pre_users = GetPreUsers()
	#get_pre_users.run()
	#os.system('adb forward tcp:6779 tcp:6779')
	while True:
		get_pre_users.run()