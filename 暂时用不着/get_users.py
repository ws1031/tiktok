import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger

class GetUsers():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()

	def get_users(self, category_id, page):
		try:
			raw_data = self.get_raw_data.get_users(category_id, page)
		except Exception as e:
			raw_data = None
			logger.error('get_users错误-' + e.args + '-category_id-' + category_id + '-page-' + page)
		if raw_data:
			sec_user_id_list = self.parse_users(raw_data)
			self.save_to_redis(sec_user_id_list)

	def parse_users(self, raw_data):
		sec_user_id_list = []
		data = raw_data.get('aweme_list')
		for each in data:
			sec_user_id = each.get('author').get('sec_uid')
			sec_user_id_list.append(sec_user_id)
		return sec_user_id_list

	def save_to_redis(self, sec_user_id_list):
		for each in sec_user_id_list:
			self.redis_client.add_users(each)

	def run(self):
		cate_list = range(-1, 15)
		for cate in cate_list:
			cate_page_list = [[cate, page] for page in range(0, 100)]
			logger.info('get_users当前爬取cate-' + str(cate))
			tasks = [gevent.spawn(self.get_users, str(cate), str(page)) for cate, page in cate_page_list]
			gevent.joinall(tasks)

if __name__ == '__main__':
	get_users = GetUsers()
	get_users.run()
