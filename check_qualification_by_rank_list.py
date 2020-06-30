#检查用户是否直播带货，如果正在直播，升级为主播

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import os
import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import STUPID_KEY_WORDS

class CheckQualificationByRankList():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.live_user_list = []
		self.room_id_list = []
		self.stupid_key_words = STUPID_KEY_WORDS

	def get_users(self):
		users = self.redis_client.get_users() #每次获取分数最低的10000个
		return users

	def is_live_user(self, sec_user_id):
		return self.redis_client.is_live_user(sec_user_id)

	def save_rooms(self):
		for each in self.room_id_list:
			self.redis_client.add_rooms(each)

	def add_to_live_users(self):
		for each in self.live_user_list:
			self.redis_client.add_live_users(each, 1)

	def increase_user_score(self, sec_user_id):
		self.redis_client.increase_user_score(sec_user_id)

	def is_qualified_user(self, user):
		nickname = user.get('nickname')
		for word in self.stupid_key_words:
			if word in nickname:
				return False
		return True

	def get_rank_list(self, sec_user_id):

		if not self.is_live_user(sec_user_id):
			try:
				raw_data = self.get_raw_data.get_rank_list(sec_user_id)
			except Exception as e:
				logger.error('get_rank_list出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
				return None

			try:
				user = raw_data.get('data').get('anchor_info').get('user')
			except Exception as e:
				logger.error('parse_current_room出错' + e.args[0] + '-sec_user_id-' + sec_user_id)
				return None

			if self.is_qualified_user(user):
				own_room = user.get('own_room')
				if own_room: #如果有这个，说明直播开始了
					room_id = own_room.get('room_ids_str')[0]
					self.live_user_list.append(sec_user_id)
					self.room_id_list.append(room_id)
				self.increase_user_score(sec_user_id)
			else:
				self.redis_client.delete_users(sec_user_id)
				logger.info('删除user-sec_user_id-' + sec_user_id)
		else:
			self.increase_user_score(sec_user_id)
		"""
		try:
			raw_data = self.get_raw_data.get_rank_list(sec_user_id)
		except Exception as e:
			logger.error('get_rank_list出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			nickname = raw_data.get('data').get('anchor_info').get('user').get('nickname')
			print(nickname)
		except Exception as e:
			logger.error('parse_current_room出错' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None
		"""

	def run(self):
		users = self.get_users()

		batch_size = 50 #这个接口80个一批可行的（总共近4000个），更多的我不敢再试了
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('当前获取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_rank_list, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

			self.save_rooms()
			self.add_to_live_users()
			logger.info('新增room_id-' + str(len(self.room_id_list)))
			self.room_id_list.clear()
			self.live_user_list.clear()

if __name__ == '__main__':
	check_qualification_by_rank_list = CheckQualificationByRankList()
	os.system('adb forward tcp:6779 tcp:6779')
	while True:
		check_qualification_by_rank_list.run()