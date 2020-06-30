import requests
import json
import time
import random

from redis_client import RedisClient

class GetRawData():
	def __init__(self):
		self.redis_client = RedisClient()
		self.gorgon_server = "http://localhost:6779/gorgon"
		self.cookie = None
		#self.user_agent = 'com.ss.android.ugc.aweme/100601 (Linux; U; Android 5.1.1; zh_CN; OPPO R11; Build/NMF26X; Cronet/TTNetVersion:3154e555 2020-03-04 QuicVersion:8fc8a2f3 2020-03-02)'
		self.user_agent = 'com.ss.android.ugc.aweme/100601 (Linux; U; Android 5.1.1; zh_CN; MI 6; Build/NMF26X; Cronet/TTNetVersion:3154e555 2020-03-04 QuicVersion:8fc8a2f3 2020-03-02)'
		
		self.common_params = {
			"os_api":"22",
			"device_type":"MI%206", #获取不到了需要抓包改，抓包抓不着就是被封了，需要换一台设备
			"ssmix":"a",
			"manifest_version_code":"100601",
			"dpi":"320",
			"uuid":"863064012409126",
			"app_name":"aweme",
			"version_name":"10.6.0",
			"app_type":"normal",
			"ac":"wifi",
			"update_version_code":"10609900",
			"channel":"aweGW",
			"device_platform":"android",
			"iid":"111280011708", #获取不到了需要抓包改，抓包抓不着就是被封了，需要换一台设备
			"version_code":"100600",
			"cdid":"bdf6e59a-1c6c-4ca7-9745-7515b4b50ffb",
			"openudid":"2405bd8d333e9804",
			"device_id":"70361550255", #获取不到了需要抓包改，抓包抓不着就是被封了，需要换一台设备
			"resolution":"900*1600",
			"os_version":"5.1.1",
			"language":"zh",
			"device_brand":"HUAWEI",
			"aid":"1128",
		}

	def get_raw_data(self, base_url, params, method='get', data=None):
		url = base_url + '&'.join(['='.join([a, b]) for a, b in params.items()])
		headers = {
			"content-type": "application/json;charset=utf-8"
		}
		response = requests.post(self.gorgon_server, data = json.dumps({'url': url}), headers = headers, timeout = 5)
		result = json.loads(response.content)
		headers = {
			'User-Agent': self.user_agent,
			'X-Gorgon': result.get('X-Gorgon'),
			'X-Khronos': result.get('X-Khronos')
		}

		if base_url in ['https://api3-core-c-hl.amemv.com/aweme/v1/user/profile/other/?', 'https://api3-normal-c-hl.amemv.com/aweme/v1/multi/aweme/detail/?']:
			if not self.cookie:
				self.cookie = self.redis_client.get_params('dy_cookie')
				#self.cookie = 'install_id=111280011708; ttreq=1$155f70f34017463054b07a1ddeab852ca3c3243b; odin_tt=5455854fecdb80efe8fe292bbdbcdb3116c045cda77792677708ba27aa353d44c895ea5667734d919036b345d2ff12ae2c73f582f4e35058e8f9ff7a75b8fe1b'
				#self.cookie = 'odin_tt=5e12571923cb1b635f6abc384f3997026806435094ac5fcc950009b8c811c82dbf8464957adf80cab4af35b5a5d4dbf8a8036825f75899f67224ee220b308c25; install_id=2172274732445896; ttreq=1$596ed4a4d3cc39fbf271b936a59a706c65f565d4'
			headers.update({"Cookie": self.cookie})

		if method == 'get':
			#print(url)
			response = requests.get(url, headers=headers)

		elif method == 'post':
			response = requests.post(url, headers=headers, data=data)
		return response.json()

	def get_following(self, sec_user_id): #获取用户关注的其他其他用户，如果不可见，返回的是{"status_code": 2096, "log_pb": {"impr_id": "202005281507330101440611040D113D66"}, "extra": {"logid": "202005281507330101440611040D113D66", "now": 1590649653460, "fatal_item_ids": []}}
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://aweme-hl.snssdk.com/aweme/v1/user/following/list/?'
		params = {
			#"user_id":"84990209480",
			"sec_user_id":sec_user_id,
			"max_time":ts,
			"count":"20",
			"offset":"0",
			"source_type":"1",
			"address_book_access":"2",
			"gps_access":"1",
			"vcd_count":"0",
			"vcd_auth_first_time":"0",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_user_profile(self, sec_user_id): #获取用户主页
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-core-c-hl.amemv.com/aweme/v1/user/profile/other/?'
		params = {
			"sec_user_id":sec_user_id,
			"address_book_access":"1",
			"from":"0",
			"publish_video_strategy_type":"0",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
			"oaid":"00000000-0000-0000-0000-000000000000"
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_clips(self, aweme_id_list): #批量获取短视频数据
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		aweme_id_json = json.dumps(aweme_id_list)
		aweme_ids = aweme_id_json.replace(' ', '').replace('[', '%5b').replace(']', '%5d').replace(',', '%2c')
		#print(aweme_ids)
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/multi/aweme/detail/?'
		params = {
			"aweme_ids":aweme_ids,
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_clips_h5(self, aweme_id_list): #从h5端批量获取短视频数据
		base_url = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?'
		aweme_id_json = json.dumps(aweme_id_list)
		aweme_ids = aweme_id_json.replace(' ', '').replace('[', '').replace(']', '')
		url = base_url + 'item_ids=' + aweme_ids
		result = requests.get(url)
		return result.json()

	#def get_promotions(self, user_id, sec_user_id):
	def get_promotions(self, sec_user_id): #获取商品橱窗
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/promotion/user/promotion/list/?'
		params = {
			"count":"1000",
			"cursor":"0",
			#"user_id":user_id,
			"column_id":"0",
			"sort":"0",
			"sec_user_id":sec_user_id,
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_rank_list(self, sec_user_id): #获取用户某项排名，这里用来确定直播是否开始
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://webcast3-normal-c-hl.amemv.com/webcast/ranklist/hour/?'
		params = {
			"hour_info":"1",
			#"room_id":"6828395212583209743",
			"rank_type":"12",
			"sec_anchor_id":sec_user_id,
			"anchor_id":"102987709723",
			"webcast_sdk_version":"1470",
			"webcast_language":"zh",
			"webcast_locale":"zh_CN",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_live(self, room_id): #获取直播
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://webcast3-normal-c-hl.amemv.com/webcast/room/info/?'
		params = {
			"pack_level":"4",
			"room_id":room_id,
			"webcast_sdk_version":"1470",
			"webcast_language":"zh",
			"webcast_locale":"zh_CN",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007"
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_item_list(self, sec_author_id, room_id): #获取直播商品列表
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://lianmengapi-hl.snssdk.com/live/promotions/?'
		params = {
			#"author_id":"1272709026",
			"sec_author_id":sec_author_id,
			"room_id":room_id,
			#"entrance_info":"%257B%2522request_id%2522%253A%25222020042418154001002207014700940336%2522%252C%2522sdk_version%2522%253A%25221470%2522%252C%2522action_type%2522%253A%2522draw%2522%252C%2522room_id%2522%253A%25226819214164456639232%2522%252C%2522_param_live_platform%2522%253A%2522live%2522%252C%2522enter_from_merge%2522%253A%2522live_merge%2522%252C%2522anchor_id%2522%253A%2522102669364918%2522%252C%2522enter_method%2522%253A%2522live_cover%2522%252C%2522follow_status%2522%253A%25220%2522%252C%2522enter_from%2522%253A%2522live%2522%252C%2522category_name%2522%253A%2522live_merge_temai_live_cover%2522%252C%2522carrier_type%2522%253A%2522live_list_card%2522%257D",
			"first_enter":"false",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

if __name__ == '__main__':
	get_raw_data = GetRawData()
	sec_user_id = 'MS4wLjABAAAArEKjHBZqF5s-Gia8ctxea85CYV45L3EtISsbo_r0tSQ'
	#sec_user_id = 'MS4wLjABAAAAv9Yli8kz8wC1Rs6ua2cF4X7Z-k4Vq1LJiQv3lTHShzjwDZeVFoTdjUv_avt_g4cL'
	#sec_user_id = 'MS4wLjABAAAA-26N9YCbI1Dc0xZA2u6Gm3ZaneAZ897lkIwPA-r7k5g'
	category_id = '4'
	page = '4'
	aweme_id = '6761959638050082052'
	room_id = '6831405347828140800'
	aweme_id_list = [6827305365315538187, 6736474010072272141]

	#data = get_raw_data.get_following(sec_user_id)

	#data = get_raw_data.get_rank_list(sec_user_id)
	#data = get_raw_data.get_live(room_id)
	#data = get_raw_data.get_item_list(sec_user_id, room_id)

	#data = get_raw_data.get_user_profile(sec_user_id)
	data = get_raw_data.get_promotions(sec_user_id)
	#data = get_raw_data.get_clips(aweme_id_list)

	#data = get_raw_data.get_videos(sec_user_id)
	#data = get_raw_data.get_video(aweme_id)
	#data = get_raw_data.get_fans(sec_user_id)
	#data = get_raw_data.get_channel()
	#data = get_raw_data.get_users(category_id, page)
	#data = get_raw_data.get_search_user()
	#data = get_raw_data.get_user_dongtai(sec_user_id)
	#data = get_raw_data.get_current_room(sec_user_id)
	#data = get_raw_data.get_promotions(user_id, sec_user_id)

	print(json.dumps(data, ensure_ascii=False))


"""
	def get_user_dongtai(self, sec_user_id): #获取用户动态
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/forward/list/?'
		params = {
			#"user_id":"102987709723",
			"sec_user_id":sec_user_id,
			"max_cursor":"0",
			"min_cursor":"0",
			"count":"20",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)


	def get_video(self, aweme_id): #获取短视频数据
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/aweme/detail/?'
		params = {
			"aweme_id":aweme_id,
			"origin_type":"store_page",
			"request_source":"0",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)		

	def get_videos(self, sec_user_id): #获取某个用户的短视频数据
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-core-c-hl.amemv.com/aweme/v1/aweme/post/?'
		params = {
			"source":"0",
			"publish_video_strategy_type":"1",
			"max_cursor":str(int(ts)*1000),
			"sec_user_id":sec_user_id,
			"count":"25",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_users(self, category_id, page): #获取用户，本来用来积累数据
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v2/shop/discovery/feed/?'
		params = {
			"request_tag_from":"rn",
			"area_id":"2",
			"category_id":category_id,
			"page":page,
			"size":"12",
			"source_page":"shopping_assistant",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007 ",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_fans(self, sec_user_id): #获取用户粉丝
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://api3-normal-c-hl.amemv.com/aweme/v1/user/follower/list/?'
		params = {
			#"user_id":"58867705068",
			"sec_user_id":sec_user_id,
			"max_time":ts,
			"count":"60",
			"offset":"0",
			"source_type":"1",
			"address_book_access":"1",
			"gps_access":"1",
			"vcd_count":"0",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_channel(self): #获取推荐直播，本来用来积累数据
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://webcast3-core-c-hl.amemv.com/webcast/feed/?'
		params = {
			"cate_id":"0",
			"channel_id":"21",
			"content_type":"0",
			"req_type":"0",
			"show_location":"0",
			"style":"2",
			"sub_channel_id":"0",
			"sub_type":"live_merge",
			"tab_id":"1",
			"type":"live",
			"max_time":str(int(time.time()*1000)-random.randint(0,10)*1000),
			"req_from":"feed_loadmore",
			"webcast_sdk_version":"1470",
			"webcast_language":"zh",
			"webcast_locale":"zh_CN",
			"ts":ts,
			"host_abi":"armeabi-v7a",
			"_rticket":_rticket,
			"mcc_mnc":"46007"
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_current_room(self, sec_user_id): #获取用户当前直播间id，本来用来确定直播是否开始
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://webcast3-normal-c-hl.amemv.com/webcast/user/?'
		params = {
			"request_from":"admin",
			#"current_room_id":"6828395212583209743",
			#"target_uid":"102987709723",
			#"sec_anchor_id":"MS4wLjABAAAAltkywr0wrBncyLxQP1qu02EIinqkkiB1gb3yKkuPP-w",
			#"anchor_id":"102987709723",
			"sec_target_uid":sec_user_id,
			"packed_level":"2",
			"webcast_sdk_version":"1470",
			"webcast_language":"zh",
			"webcast_locale":"zh_CN",
			"ts":"1589868122",
			"host_abi":"armeabi-v7a",
			"_rticket":"1589868120562",
			"mcc_mnc":"46007",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params)

	def get_search_general(self): #搜索综合
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://search-lf.amemv.com/aweme/v1/general/search/single/?'
		params = {
			'ts': ts,
			'host_abi': 'armeabi-v7a',
			'_rticket': _rticket,
			'mcc_mnc': '46007',
		}
		data = {
			"keyword":"chboss",
			"offset":"0",
			"count":"20",
			"is_pull_refresh":"0",
			"search_source":"search_sug",
			"hot_search":"0",
			"latitude":"30.998872478837285",
			"longitude":"115.56876259314306",
			"search_id":"",
			"query_correct_type":"1",
			"mac_address":"40%3A5B%3AD8%3AD3%3A33%3AE9",
			"is_filter_search":"0",
			"sort_type":"0",
			"publish_time":"0",
			"disable_synthesis":"0",
			"multi_mod":"0",
			"single_filter_aladdin":"0",
			"client_width":"450",
			"dynamic_type":"0",
			"epidemic_card_type":"0",
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params, method='post', data=data)

	def get_search_user(self): #搜索用户
		ts = str(int(time.time()))
		_rticket = str(int(time.time()*1000))
		base_url = 'https://search-lf.amemv.com/aweme/v1/discover/search/?'
		params = {
			'ts': ts,
			'host_abi': 'armeabi-v7a',
			'_rticket': _rticket,
			'mcc_mnc': '46007',
		}
		data = {
			'cursor': '0',
			'keyword': 'chboss',
			'count': '10',
			'type': '1',
			'is_pull_refresh': '1',
			'hot_search': '0',
			'search_source': '',
			'search_id': '',
			'query_correct_type': '1'
		}
		params.update(self.common_params)

		return self.get_raw_data(base_url, params, method='post', data=data)
"""