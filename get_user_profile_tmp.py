import gevent
import gevent.monkey
gevent.monkey.patch_all()

import time
import json
#获取live_users的profile信息

from config import STUPID_KEY_WORDS

from get_raw_data import GetRawData
from redis_client import RedisClient
from logger import logger
from config import FILE_DIRECTORY

class GetUserProfile():
	def __init__(self):
		self.get_raw_data = GetRawData()
		self.redis_client = RedisClient()
		self.stupid_key_words = STUPID_KEY_WORDS

	def get_users(self):
		users = self.redis_client.test_b()
		return users

	def get_user_profile(self, sec_user_id):
		try:
			raw_data = self.get_raw_data.get_user_profile(sec_user_id)
		except Exception as e:
			logger.error('get_user_profile出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		try:
			user_profile = self.parse_user_profile(raw_data)
		except Exception as e:
			logger.error('parse_user_profile出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None

		if user_profile:
			self.write_to_file(json.dumps(user_profile, ensure_ascii=False))
			self.redis_client.test_c(sec_user_id)

	def is_qualified_user(self, user):
		nickname = user.get('nickname')
		for word in self.stupid_key_words:
			if word in nickname:
				logger.info('stupid key word:' + word)
				return False
		if user.get('is_gov_media_vip'):
			logger.info('government media verification')
			return False
		if user.get('enterprise_verify_reason') != '':
			logger.info('enterprise media verification')
			return False
		if user.get('custom_verify') != '':
			logger.info('other verification')
			return False
		if not user.get('with_fusion_shop_entry'):
			logger.info('no shop entry')
			return False
		if not user.get('live_commerce'):
			logger.info('no live')
			return False
		if not user.get('with_commerce_entry'):
			logger.info('no commerce entry')
			return False
		return True

	def parse_user_profile(self, raw_data):
		data = raw_data.get('user')
		user_profile = {}
		user_profile['sec_uid'] = data.get('sec_uid')
		if self.is_qualified_user(data):
			user_profile['follower_count'] = data.get('follower_count')
			user_profile['nickname'] = data.get('nickname')	
			user_profile['gender'] = data.get('gender')
			user_profile['location'] = data.get('location')
			user_profile['birthday'] = data.get('birthday')
			user_profile['avatar_url'] = data.get('avatar_larger').get('url_list')[0]
			user_profile['school_name'] = data.get('school_name')
			user_profile['signature'] = data.get('signature')
			user_profile['uid'] = data.get('uid')
			user_profile['short_id'] = data.get('short_id')
			user_profile['unique_id'] = data.get('unique_id')	
			user_profile['star_atlas'] = data.get('commerce_user_info').get('star_atlas')
			user_profile['aweme_count'] = data.get('aweme_count')
			user_profile['dongtai_count'] = data.get('dongtai_count')
			user_profile['following_count'] = data.get('following_count')
			user_profile['favoriting_count'] = data.get('favoriting_count')	
			user_profile['total_favorited'] = data.get('total_favorited')
			user_profile['live_commerce'] = data.get('live_commerce')
			user_profile['create_time'] = str(int(time.time()))
			return user_profile

		else:
			sec_user_id = user_profile['sec_uid']
			self.redis_client.delete_users(sec_user_id)
			self.redis_client.delete_live_users(sec_user_id)
			self.redis_client.test_c(sec_user_id)
			#print(json.dumps(raw_data, ensure_ascii=False))
			logger.info('删除user-sec_user_id-' + usec_user_id)
			return None

	def write_to_file(self, user_profile):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'user_profiles'+ '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(user_profile + '\n')

	def run(self):
		users = self.get_users()
		logger.info('共有users-' + str(len(users)))
		batch_size = 1 #50个会获取不到数据
		for batch_limit in range(0, len(users), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(users))
			logger.info('当前爬取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_user_profile, sec_user_id) for sec_user_id in users[start:stop]]
			gevent.joinall(tasks)

if __name__ == '__main__':
	get_user_profile = GetUserProfile()
	get_user_profile.run()