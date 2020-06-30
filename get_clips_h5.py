import gevent
import gevent.monkey
gevent.monkey.patch_all()

import requests
import time
import json

from get_raw_data import GetRawData
from logger import logger
from redis_client import RedisClient
from config import FILE_DIRECTORY

class GetClipsH5():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()

	def get_aweme_lists(self):
		aweme_lists = []
		awemes = self.redis_client.get_awemes()
		for i in range(0, len(awemes), 20):
			aweme_list = awemes[i:i+20]
			aweme_lists.append(aweme_list)
		return aweme_lists

	def get_clips_h5(self, aweme_list):
		aweme_int_list =  [int(aweme) for aweme in aweme_list]
		try:
			raw_data = self.get_raw_data.get_clips_h5(aweme_int_list)
		except Exception as e:
			logger.error('get_clips_h5出错-' + e.args[0])
			return None

		if raw_data.get('status_code') != 2053:
			try:
				clips = self.parse_clips_h5(raw_data)
			except Exception as e:
				logger.error('parse_clips_h5出错-' + e.args[0])
				return None

			if len(clips) != 0: #忘记这个if语句是出于什么目的了，可能是因为一批aweme中可能会有一些不是视频吧。
				self.write_to_file(json.dumps(clips, ensure_ascii=False))
				for each in aweme_list:
					self.redis_client.delete_awemes(each)
			else:
				logger.error('该组clips数量为0')

		else:
			logger.error('status_code 2053，一整批都不是视频')

	def parse_clips_h5(self, raw_data):
		clips = []
		data = raw_data.get('item_list')
		for each in data:
			clip = {}
			clip['aweme_share_url'] = each.get('share_url')
			clip['user_id'] = each.get('author_user_id')
			clip['aweme_duration'] = each.get('duration')
			clip['aweme_time'] = each.get('create_time')
			clip['aweme_id'] = each.get('aweme_id')

			video = each.get('video')
			clip['aweme_cover'] = video.get('cover').get('url_list')[0]
			clip['aweme_url'] = video.get('play_addr').get('url_list')[0]

			author = each.get('author')
			if author:
				clip['user_nickname'] = author.get('nickname')
				clip['user_avatar'] = author.get('avatar_larger').get('url_list')[0]
				clip['user_short_id'] = author.get('short_id')
				clip['user_signature'] = author.get('signature')
				clip['user_unique_id'] = author.get('unique_id')
			else:
				logger.error('未获取到author')

			statistics = each.get('statistics')
			clip['comment_count'] = statistics.get('comment_count')
			clip['like_count'] = statistics.get('digg_count')

			clips.append(clip)

		return clips

	def write_to_file(self, clips):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'clips_h5' + '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(clips + '\n')

	def run(self):
		aweme_lists = self.get_aweme_lists()
		logger.info('共有aweme组数：' + str(len(aweme_lists)))
		batch_size = 200
		for batch_limit in range(0, len(aweme_lists), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(aweme_lists))
			logger.info('get_clips_h5爬取当前aweme组序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_clips_h5, aweme_list) for aweme_list in aweme_lists[start:stop]]
			gevent.joinall(tasks)


if __name__ == '__main__':
	get_clips_h5 = GetClipsH5()
	get_clips_h5.run()