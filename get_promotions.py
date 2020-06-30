import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json
import random

from get_raw_data import GetRawData
from logger import logger
from redis_client import RedisClient
from config import FILE_DIRECTORY

class GetPromotions():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.aweme_id_list = []

	def get_users(self):
		users = self.redis_client.get_users()
		return users

	def get_promotions(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_promotions(sec_user_id)
		except Exception as e:
			logger.error('get_promotions出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			promotions = self.parse_promotions(raw_data, sec_user_id)
		except Exception as e:
			logger.error('parse_promotions错误-' + e.args + '-sec_user_id-' + sec_user_id)
			return None

		self.write_to_file(json.dumps(promotions, ensure_ascii=False))

	def parse_promotions(self, raw_data, sec_user_id):
		promotions = []
		data = raw_data.get('promotions')
		if data == []:
			logger.info('该用户不带货，将删除，sec_user_id-' + sec_user_id)
			self.redis_client.delete_users(sec_user_id)
			return None
		else:
			for each in data:
				promotion = {}
				#promotion['user_id'] = user_id
				promotion['sec_user_id'] = sec_user_id
				promotion['price'] = each.get('price')/100
				promotion['cover_url'] = each.get('images')[0].get('url_list')[0]
				promotion['title'] = each.get('title')
				promotion['product_id'] = each.get('product_id')
				promotion['product_url'] = each.get('detail_url')
				promotion['min_price'] = str(int(each.get('min_price'))/100)
				promotion['douyin_sales'] = each.get('sales')
				promotion['product_source'] = each.get('goods_source')
				promotion['create_time'] = str(int(time.time()))

				if each.get('market_price'):
					promotion['market_price'] = each.get('market_price')/100

				if each.get('last_aweme_id'):
					promotion['promotion_type'] = 'video'
					promotion['aweme_id'] = int(each.get('last_aweme_id'))
					self.aweme_id_list.append(promotion['aweme_id'])
				else:
					promotion['promotion_type'] = 'picture'

				if each.get('taobao'):
					taobao = each.get('taobao')
					if taobao.get('coupon'):
						promotion['coupon_amount'] = taobao.get('coupon').get('coupon_amount')
						promotion['price_after_coupon'] = promotion['price'] - float(promotion['coupon_amount'])
						promotion['coupon_url'] = taobao.get('coupon').get('coupon_web_url')

				promotions.append(promotion)
			return promotions

	def write_to_file(self, promotions):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		harry_potter = str(random.choice(range(100)))
		with open (FILE_DIRECTORY + '/' + 'promotions' + '_' + harry_potter + '.txt', 'a', encoding='utf-8') as file:
			file.write(promotions + '\n')

	def save_awemes(self):
		for each in self.aweme_id_list:
			self.redis_client.add_awemes(each)

	def run(self):
		users = self.get_users()
		logger.info('共有用户数量：' + str(len(users)))
		batch_size = 50 #尽管异步，还是很慢，200个就很慢很慢了，慢到跟同步一样，这可能是抖音某个神奇的特点吧
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('get_promotions爬取当前用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_promotions, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

			self.save_awemes()
			self.aweme_id_list.clear()

if __name__ == '__main__':
	get_promotions = GetPromotions()
	get_promotions.run()