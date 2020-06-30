import gevent
import gevent.monkey
gevent.monkey.patch_all()

import json
import time

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import FILE_DIRECTORY

class GetLives():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.lives_off_list = []

	def get_rooms(self):
		return self.redis_client.get_rooms()

	def delete_rooms(self): #直播结束了，就将用户的状态改回0，删除room_id，并添加item_list记录
		for each in self.lives_off_list:
			room_id = each.split('_', 1)[0]
			sec_user_id = each.split('_', 1)[1]
			self.redis_client.add_live_users(sec_user_id, 0)
			self.redis_client.delete_rooms(room_id)
			self.redis_client.add_item_lists(each)

	def get_lives(self, room_id):
		try:
			live_raw_data = self.get_raw_data.get_live(room_id)
		except Exception as e:
			logger.error('get_live出错-' + e.args[0] + '-room_id-' + room_id)
			return None
		try:
			live_info = self.parse_lives(live_raw_data, room_id)
		except Exception as e:
			logger.error('parse_lives出错-' + e.args[0] + '-room_id-' + room_id)
			return None
			
		self.write_to_file(live_info)
		if live_info['status'] == 4: #写入文件成功之后才删除
			self.lives_off_list.append(live_info['room_id'] + '_' + live_info['sec_user_id'])

	def parse_lives(self, live_raw_data, room_id):
		data = live_raw_data.get('data')
		live_info = {}
		live_info['room_id'] = room_id
		live_info['start_time'] = data.get('create_time') #直播开始时间
		live_info['like_count'] = data.get('like_count')
		live_info['share_url'] = data.get('share_url')
		live_info['title'] = data.get('title')
		live_info['status'] = data.get('status') #2为正在直播，4为直播结束
		live_info['viewer_count'] = data.get('user_count') #实时观看人数
		live_info['cover_url'] = data.get('cover').get('url_list')[0]

		owner = data.get('owner')
		live_info['avatar_url'] = owner.get('avatar_large').get('url_list')[0] 
		live_info['city'] = owner.get('city')
		live_info['follower_count'] = owner.get('follow_info').get('follower_count') 
		live_info['gender'] = owner.get('gender')
		live_info['short_id'] = owner.get('short_id') #主播短id
		live_info['id'] = owner.get('id_str') #主播长id
		live_info['nickname'] = owner.get('nickname')
		live_info['signature'] = owner.get('signature')
		live_info['short_id'] = owner.get('short_id')
		live_info['sec_user_id'] = owner.get('sec_uid') 
		#live_info['mobile'] = owner.get('telephone') #主播手机
		live_info['ticket_count'] = owner.get('ticket_count') #主播总音浪
		live_info['create_time'] = str(int(time.time())) #记录时间

		stats = data.get('stats')
		live_info['fan_ticket'] = stats.get('fan_ticket') #本场收入音浪
		live_info['follow_count'] = stats.get('follow_count') #本场关注
		live_info['gift_count'] = stats.get('gift_uv_count') #本场获得礼物
		live_info['total_viewer'] = stats.get('total_user') #总观看人数

		return live_info

	def write_to_file(self, live_info):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'lives' + '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(json.dumps(live_info, ensure_ascii=False) + '\n')

	def run(self):
		all_room_ids = self.get_rooms()
		logger.info('此前正在直播的直播间数量：' + str(len(all_room_ids)))
		batch_size = 150 #本地200可以，云手机200不行
		for batch_limit in range(0, len(all_room_ids), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(all_room_ids))
			logger.info('待查看并获取的此前正在直播的直播间-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_lives, room_id) for room_id in all_room_ids[start:stop]]
			gevent.joinall(tasks)

			logger.info('新发现已结束的直播数量-' + str(len(self.lives_off_list)))
			self.delete_rooms()
			self.lives_off_list.clear()

if __name__ == '__main__':
	get_lives = GetLives()
	get_lives.run()




