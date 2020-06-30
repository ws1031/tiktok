import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger

class GetCurrentRoom():
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

	def get_current_room(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_current_room(sec_user_id)
		except Exception as e:
			logger.error('get_current_room出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try: 
			check = raw_data.get('data').get('pay_grade').get('grade_describe')
		except Exception as e:
			logger.error('parse_current_room出错' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		own_room = raw_data.get('data').get('own_room')
		if own_room: #如果有这个，说明直播以及开始了
			room_id = own_room.get('room_ids_str')[0]
			self.room_id_list.append(room_id)
			logger.info(sec_user_id + '-正在直播，room_id-' + room_id)
		else:
			logger.info(sec_user_id + '-未在直播')

	def run(self):
		users = self.get_users()
		logger.info('共有users-' + str(len(users)))
		batch_size = 20
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('当前爬取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_current_room, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

		#self.save_rooms()

if __name__ == '__main__':
	get_current_room = GetCurrentRoom()
	get_current_room.run()