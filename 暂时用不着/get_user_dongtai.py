import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger

class GetUserDongtai():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.room_id_list = []

	def get_users(self):
		users = self.redis_client.get_users()
		return users

	def save_rooms(self):
		for each in self.room_id_list:
			self.redis_client.add_rooms(each, 0)

	def get_user_dongtai(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_user_dongtai(sec_user_id)
		except Exception as e:
			logger.error('get_user_dongtai出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			self.parse_user_dongtai(raw_data)
		except Exception as e:
			logger.error('parse_user_dongtai出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)

	def parse_user_dongtai(self, raw_data):
		data = raw_data.get('dongtai_list')[0]
		room_id = data.get('aweme').get('author').get('room_id')
		if room_id != 0:
			self.room_id_list.append(str(room_id))
			logger.info('该主播已开始直播，room_id-' + str(room_id))
		else:
			logger.info('该主播尚未开始直播')

	def run(self):
		users = self.get_users()
		logger.info('共有users-' + str(len(users)))
		batch_size = 20 #20个也获取不到数据
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('当前爬取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_user_dongtai, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

		#self.save_rooms()

if __name__ == '__main__':
	get_user_dongtai = GetUserDongtai()
	get_user_dongtai.run()