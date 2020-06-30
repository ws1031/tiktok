import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import time

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger


class GetRooms():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.sec_user_id_list = []
		self.room_id_list = []

	def get_channel(self):
		try:
			channel_raw_data = self.get_raw_data.get_channel()
		except Exception as e:
			logger.error('get_channel出错-' + e.args[0])
			return None

		try:
			self.parse_channel(channel_raw_data)
		except Exception as e:
			logger.error('parse_channel出错-' + e.args[0])
			return None

		#logger.info(json.dumps([i[-10:-1] for i in self.sec_user_id_list]))
		for each in self.room_id_list:
			self.redis_client.add_rooms(each)
		for each in self.sec_user_id_list:
			self.redis_client.add_users(each, 1)

	def parse_channel(self, channel_raw_data):
		for each in channel_raw_data.get('data'):
			room_id = each.get('data').get('id_str')
			sec_user_id = each.get('data').get('owner').get('sec_uid')
			follower = each.get('data').get('owner').get('follow_info').get('follower_count')

			if follower >= 10000:
				try:
					item_list = self.get_raw_data.get_item_list(sec_user_id, room_id)
				except Exception as e:
					logger.error('get_item_list出错-' + e.args[0])
					return None

				if len(item_list.get('promotions')) != 0:
					self.room_id_list.append(room_id)
					self.sec_user_id_list.append(sec_user_id)
		
	def run(self):
		tasks = [gevent.spawn(self.get_channel) for i in range(1)]
		gevent.joinall(tasks)
		logger.info('本批次共获得room_id和sec_user_id-' + str(len(self.sec_user_id_list)) + '-' + str(len(self.room_id_list)))
		self.sec_user_id_list.clear()
		self.room_id_list.clear()

if __name__ == '__main__':
	#get_rooms = GetRooms()
	#get_rooms.run()
	while True:
		get_rooms = GetRooms()
		while True:
			get_rooms.run()