#将飞瓜获取来的aweme_id兑换为抖音sec_user_id

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import requests
import time
import json

from get_raw_data import GetRawData
from logger import logger
from redis_client import RedisClient

class GetSecUserIds():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()

	def get_aweme_lists(self):
		offset = 20
		aweme_lists = []
		awemes = self.redis_client.get_feigua_awemes()
		for i in range(0, len(awemes), offset):
			aweme_list = awemes[i:i+offset]
			aweme_lists.append(aweme_list)
		return aweme_lists

	def get_clips(self, aweme_list):
		sec_user_id_list = []
		aweme_id_list = []
		aweme_int_list =  [int(aweme) for aweme in aweme_list]
		try:
			raw_data = self.get_raw_data.get_clips(aweme_int_list)
		except Exception as e:
			logger.error('get_clips出错-' + e.args[0])
			return None

		if raw_data.get('status_code') == 2053:
			logger.info('这组没有视频')
		else:
			data = raw_data.get('aweme_details')
			for each in data:
				aweme_id = each.get('aweme_id')
				sec_user_id = each.get('author').get('sec_uid')
				if sec_user_id:
					aweme_id_list.append(aweme_id)
					sec_user_id_list.append(sec_user_id)
			for each in aweme_id_list:
				self.redis_client.delete_feigua_awemes(each)
			for each in sec_user_id_list:
				self.redis_client.add_pre_users(each, -1)

	def run(self):
		aweme_lists = self.get_aweme_lists()
		logger.info('共有feigua_aweme组数：' + str(len(aweme_lists)))
		batch_size = 1
		for batch_limit in range(0, len(aweme_lists), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(aweme_lists))
			logger.info('get_clips爬取当前feigua_aweme组序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_clips, aweme_list) for aweme_list in aweme_lists[start:stop]]
			gevent.joinall(tasks)

if __name__ == '__main__':
	get_sec_user_dis = GetSecUserIds()
	get_sec_user_dis.run()