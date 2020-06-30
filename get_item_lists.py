import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import time

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import FILE_DIRECTORY

class GetItemLists():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.item_lists_saved_list = []
		self.item_list = []

	def get_room_sec_ids(self):
		return self.redis_client.get_item_lists()

	def delete_item_lists(self):
		for each in self.item_lists_saved_list:
			self.redis_client.delete_item_lists(each)

	def save_items(self):
		self.redis_client.add_items(self.item_list)

	def get_item_lists(self, room_sec_ids):
		ids = room_sec_ids.split('_', 1)
		room_id = ids[0]
		sec_user_id = ids[1]

		try:
			item_list_raw_data = self.get_raw_data.get_item_list(sec_user_id, room_id)
		except Exception as e:
			logger.error('get_item_list出错-' + e.args[0] + '-room_sec_ids-' + room_sec_ids)
			return None

		try: 
			item_list = self.parse_item_lists(item_list_raw_data, room_id, sec_user_id)
		except Exception as e:
			logger.error(room_sec_ids + '-parse_item_list失败-' + e.args[0])
			return None

		if len(item_list) != 0: #表示这场直播挂商品了
			self.write_to_file(json.dumps(item_list, ensure_ascii=False)) #先写入，再删除，没毛病
		self.item_lists_saved_list.append(room_sec_ids)

	def parse_item_lists(self, item_list_raw_data, room_id, sec_user_id):
		item_list = []
		data = item_list_raw_data.get('promotions')
		for item in data:
			item_info = {}
			item_info['room_id'] = room_id
			item_info['sec_user_id'] = sec_user_id
			item_info['title'] = item.get('title')
			item_info['short_title'] = item.get('short_title')
			item_info['product_id'] = item.get('product_id')
			item_info['promotion_id'] = item.get('promotion_id')
			item_info['price'] = item.get('price')/100
			item_info['min_price'] = item.get('min_price')/100
			item_info['item_source'] = item.get('platform_label')
			item_info['shop_id'] = item.get('shop_id')
			item_info['item_type'] = item.get('item_type')
			item_info['cover'] = item.get('cover')
			item_info['index'] = item.get('index')

			coupon_info = item.get('coupons')
			if coupon_info:
				item_info['coupon_tag'] = coupon_info[0].get('tag')
				item_info['coupon_url'] = coupon_info[0].get('coupon_url')

			item_list.append(item_info)
			self.item_list.append(item_info['promotion_id'] + '_' + room_id + '_' + sec_user_id)
		return item_list

	def write_to_file(self, item_list):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'item_lists' + '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(item_list + '\n')

	def run(self):
		all_room_sec_ids = self.get_room_sec_ids()
		logger.info('此前已结束直播并需要获取商品信息的直播间数量：' + str(len(all_room_sec_ids)))
		batch_size = 200
		for batch_limit in range(0, len(all_room_sec_ids), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(all_room_sec_ids))
			logger.info('待获取的商品所对应的直播间-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_item_lists, room_sec_ids) for room_sec_ids in all_room_sec_ids[start:stop]]
			gevent.joinall(tasks)

			logger.info('新获取商品列表/未挂商品的直播间数量-' + str(len(self.item_lists_saved_list)))
			logger.info('新获取商品的数量-' + str(len(self.item_list)))
			self.save_items() #可能是这个拖慢了速度，得想办法
			self.delete_item_lists()
			self.item_lists_saved_list.clear()
			self.item_list.clear()

if __name__ == '__main__':
	get_item_list = GetItemLists()
	get_item_list.run()