#检查pre_users中的user是否橱窗超过10个商品，是的话才能晋升为user

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import sys
import os
import time
import json

from get_raw_data import GetRawData
from logger import logger
from redis_client import RedisClient

class CheckQualificationByPromotion():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.batch_size = 50

	def get_pre_users(self):
		batch = []
		while len(batch) < self.batch_size:
			pre_user = self.redis_client.get_pre_users()
			if not self.is_user(pre_user): #如果这个pre_user在user表中还不存在
				batch.append(pre_user)
		return batch

	def count_pre_users(self):
		return self.redis_client.count_pre_users()

	def is_user(self, sec_user_id):
		return self.redis_client.is_user(sec_user_id)

	def check_qualification_by_promotion(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_promotions(sec_user_id)
		except Exception as e:
			logger.error('get_promotions出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			raw_data.get('columns')[0].get('name') #表示确实获取到了页面
			data = raw_data.get('promotions')
			if len(data) > 10: #确实获取到了页面，promotion大于10
				self.redis_client.add_users(sec_user_id)
		except Exception as e:
			logger.error('解析promotions页面失败-sec_user_id-' + sec_user_id + '-' + e.args[0])

	def run(self):
		if self.count_pre_users() > 0:
			batch = self.get_pre_users()
			tasks = [gevent.spawn(self.check_qualification_by_promotion, sec_user_id) for sec_user_id in batch]
			gevent.joinall(tasks)
		else:
			logger.info('pre_users列表空了，程序退出')
			sys.exit()

if __name__ == '__main__':
	check_qualification_by_promotion = CheckQualificationByPromotion()
	os.system('adb forward tcp:6779 tcp:6779')
	while True:
		check_qualification_by_promotion.run()