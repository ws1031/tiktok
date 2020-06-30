#检查主播是否开始直播

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger

class GetRankList():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.user_list = []
		self.room_id_list = []

	def get_users(self):
		users = self.redis_client.get_live_users(0, 0)
		return users

	def save_rooms(self):
		for each in self.room_id_list:
			self.redis_client.add_rooms(each)

	def change_user_status(self):
		for each in self.user_list:
			self.redis_client.add_live_users(each, 1)

	def get_rank_list(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_rank_list(sec_user_id)
		except Exception as e:
			logger.error('get_rank_list出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try: 
			own_room = raw_data.get('data').get('anchor_info').get('user').get('own_room')
		except Exception as e:
			logger.error('parse_current_room出错' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		if own_room: #如果有这个，说明直播开始了
			room_id = own_room.get('room_ids_str')[0]
			self.user_list.append(sec_user_id)
			self.room_id_list.append(room_id)
			#logger.info(sec_user_id + '-正在直播，room_id-' + room_id)
		#else:
			#logger.info(sec_user_id + '-未在直播')

	def run(self):
		users = self.get_users()
		logger.info('共有未在直播的users-' + str(len(users)))

		batch_size = 50 #这个接口80个一批可行的（总共近4000个），更多的我不敢再试了
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('当前获取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_rank_list, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

			self.save_rooms()
			self.change_user_status()
			logger.info('新增room_id-' + str(len(self.room_id_list)))
			self.room_id_list.clear()
			self.user_list.clear()

if __name__ == '__main__':
	get_rank_list = GetRankList()
	get_rank_list.run()