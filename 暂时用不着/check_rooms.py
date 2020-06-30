import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import time

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger

class CheckRooms():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.lives_on_list = []

	def get_rooms(self):
		return self.redis_client.get_rooms(0, 0)

	def change_room_status(self):
		for each in self.lives_on_list:
			self.redis_client.add_rooms(each, 1)

	def check_room(self, room_id):
		try:
			room_raw_data = self.get_raw_data.get_live(room_id)
		except Exception as e:
			logger.error('get_live出错-' + e.args[0] + '-room_id-' + room_id)
			return None
		try:
			owner = room_raw_data.get('data').get('owner')
			follower_count = owner.get('follow_info').get('follower_count') 
			sec_user_id = owner.get('sec_uid')
		except Exception as e:
			logger.error('解析room_raw_data出错-' + e.args[0] + '-room_id-' + room_id)
			return None

		if follower_count < 10000:
			self.redis_client.delete_users(sec_user_id)
			self.redis_client.delete_rooms(room_id)
		else:
			status = room_raw_data.get('data').get('status')
			if status == 2:
				try: #判断该场直播是否带货
					item_list_raw_data = self.get_raw_data.get_item_list(sec_user_id, room_id)
				except Exception as e:
					logger.error('get_item_list出错' + e.args[0] + '-sec_user_id和room_id-' + sec_user_id + '-' + room_id)
					return None
				if len(item_list_raw_data.get('promotions')) != 0:
					self.lives_on_list.append(room_id)

	def run(self):
		all_room_ids = self.get_rooms()
		logger.info('此前未在直播的直播间数量：'+ str(len(all_room_ids)))
		batch_size = 200
		for batch_limit in range(0, len(all_room_ids), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(all_room_ids))
			logger.info('待查看的此前未在直播的直播间-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.check_room, room_id) for room_id in all_room_ids[start:stop]]
			gevent.joinall(tasks)

			logger.info('新发现开始的直播数量-' + str(len(self.lives_on_list)))
			self.change_room_status()
			self.lives_on_list.clear()

if __name__ == '__main__':
	check_rooms = CheckRooms()
	check_rooms.run()