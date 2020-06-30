import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import time

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import FILE_DIRECTORY

class GetItems():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.saved_items_list = []

	def get_item_ids(self):
		return self.redis_client.get_items()

	def delete_items(self):
		for each in self.saved_items_list:
			self.redis_client.delete_items(each)

	def get_items(self, item):
		ids = item.split('_', 2)
		promotion_id = ids[0]
		room_id = ids[1]
		sec_user_id = ids[2]

		try:
			item_raw_data = self.get_raw_data.get_item(promotion_id)
		except Exception as e:
			logger.error('get_item出错-item-' + item)
			return None

		try:
			item_info = self.parse_items(item_raw_data, room_id, sec_user_id)
		except Exception as e:
			logger.error('parse_items出错-' + e.args[0] + '-item-'+ item)
			return None

		self.write_to_file(item_info)
		self.saved_items_list.append(item)

	def parse_items(self, item_raw_data, room_id, sec_user_id):
		item_info = {}
		item_info['room_id'] = room_id
		item_info['sec_user_id'] = sec_user_id

		item_raw_data = json.loads(item_raw_data.get('promotion'))[0]
		item_info['promotion_id'] = item_raw_data.get('promotion_id')
		item_info['product_id'] = item_raw_data.get('product_id')
		item_info['title'] = item_raw_data.get('title')
		item_info['sales'] = item_raw_data.get('sales')
		item_info['detail_url'] = item_raw_data.get('detail_url')
		item_info['image_url'] = item_raw_data.get('images')[0].get('url_list')[0]
		item_info['price'] = item_raw_data.get('price')/100

		item_info['market_price'] = ''
		market_price = item_raw_data.get('market_price')
		if market_price:
			item_info['market_price'] = market_price/100

		return item_info

	def write_to_file(self, item_info):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'items' + '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(json.dumps(item_info, ensure_ascii=False) + '\n')

	def run(self):
		all_items = self.get_item_ids()
		logger.info('共有item数量-' + str(len(all_items)))
		batch_size = 200
		for batch_limit in range(0, len(all_items), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(all_items))
			logger.info('当前获取的item-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_items, item) for item in all_items[start:stop]]
			gevent.joinall(tasks)
			logger.info('获取到items-' + str(len(self.saved_items_list)))
			self.delete_items()
			self.saved_items_list.clear()

if __name__ == '__main__':
	get_items = GetItems()
	get_items.run()
