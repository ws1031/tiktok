#新兑换来的sec_user_id状态为-1，确认带货之后，状态改为1，正式成为能产生数据的sec_user_id

import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json

from get_raw_data import GetRawData
from logger import logger
from redis_client import RedisClient

class CheckQualificationByPromotion():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()

	def get_users(self):
		users = self.redis_client.get_pre_users(-1, -1)
		return users

	def check_commercial(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_promotions(sec_user_id)
		except Exception as e:
			logger.error('get_promotions出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			raw_data.get('columns')[0].get('name') #表示确实获取到了页面
			data = raw_data.get('promotions')
			if len(data) == 0: #确实获取到了页面，promotion仍没有，那就真的不带货了
				logger.info('该用户不带货，将删除，sec_user_id-' + sec_user_id)
				self.redis_client.delete_pre_users(sec_user_id)
			else: #prrmotion是有的，说明带货，那就状态改为0
				self.redis_client.add_pre_users(sec_user_id, 0)
		except Exception as e:
			logger.error('解析promotions页面失败-sec_user_id-' + sec_user_id + '-' + e.args[0])

	def run(self):
		users = self.get_users()
		logger.info('共有待确认是否带货用户数量：' + str(len(users)))
		batch_size = 50 #尽管异步，还是很慢，200个就很慢很慢了，慢到跟同步一样，这可能是抖音某个神奇的特点吧
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('check_commercial爬取当前用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.check_commercial, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

if __name__ == '__main__':
	check_qualification_by_promotion = CheckQualificationByPromotion()
	check_qualification_by_promotion.run()