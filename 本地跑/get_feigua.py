import time
import requests
from lxml import etree
import re
import json
import redis
from urllib.parse import quote

class GetFeigua():
	def __init__(self):
		self.cookie = '_uab_collina=158804253332809761133304; chl=key=feigua2; Hm_lvt_b9de64757508c82eff06065c30f71250=1589954282,1590071627,1590110951,1590371214; ASP.NET_SessionId=1w0xd3kcnjh0pyvfw5ovkocs; SaveUserName=; FEIGUA=UserId=8149c7bcd0878bbd&NickName=a6a703c80f9f5c08fa397470e1d1c1c4a239eb57687b34b9&checksum=49e4d2b5ef8f&FEIGUALIMITID=a15fb5e26a96469897560d59452c59bf; 392550e7707338f4dc90a06f4dc76363=11c014ebad67002f7ad1f454a99db94f9264fe852e36be9e9e86a55a051dc0ecd48416c08475f24e2d217581a669d09829c81682469da84bbfee48e20831c988acf06ea4e78a2f7411719a7efd6be545bb744cf887483e621f02929265524df8f5daed19c68ddf9f2953595dd49e44e8; Hm_lpvt_b9de64757508c82eff06065c30f71250=1590557575'
		self.headers = {
			'Accept-Encoding': 'gzip, deflate, br',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Connection': 'keep-alive',
			'Cookie': self.cookie,
			'Host': 'dy.feigua.cn',
			'Referer': 'https://dy.feigua.cn/Member',
			'Sec-Fetch-Mode': 'cors',
			'Sec-Fetch-Site': 'same-origin',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36',
		}
		self.db1 = redis.StrictRedis(host='r-bp1db51661f4d0e4pd.redis.rds.aliyuncs.com', port=13457, db=2, password='U78afbZtttT678', decode_responses= True)
		self.db2 = redis.StrictRedis(host='r-bp1758aa6549c324pd.redis.rds.aliyuncs.com', port=13457, db=1, password='U78afbZtttT678', decode_responses= True)
		self.key1 = 'feigua_user_id'
		self.key2 = 'feigua_aweme_id'
		self.key3 = 'awemes'
		self.key4 = 'feigua_user_id_bak'
		self.period_list = ['day', 'month', 'week']
		self.tag_list = ['Tag', 'RiseFans', 'GrowingUp', 'Area',  'BlueV']
		#tag日周月榜走完了，RiseFans日周月榜走完了, GrowingUp日周月榜走完了, Area日榜走完了(月榜到tag,period,province,city,page:Area,month,28,342,3),  BlueV日周月榜走完了

	def get_feigua_ids(self):
		tag = self.tag_list[3]
		period = self.period_list[1]
		base_url = 'https://dy.feigua.cn/Rank/' + tag
		result = requests.get(base_url, headers=self.headers).text

		if tag == 'Area':
			last_stop = 16 #这个不能是None
			areas = json.loads(re.match('.*?areaInfos = (.*?);.*', result, re.S).group(1))
			for a, b in areas.items():
				if int(a) >= last_stop:
					for c in b.keys():
						for d in range(1, 26):
							url = base_url + '?period={0}&province={1}&city={2}&page={3}'.format(period, a, c, str(d))
							print('当前tag,period,province,city,page:{},{},{},{},{}'.format(tag, period, a, c, str(d)))
							result = requests.get(url, headers=self.headers).text
							try:
								result = json.loads(result)
								if result.get('msg') == '没有更多内容':
									print('该页没有更多内容')
									break
								if result.get('Message') == '哎呦，访问太频繁了，请稍后再试':
									print('被拦截了')
							except:
								pass
							self.parse_feigua_ids(result, d)

		else:
			last_stop = '时尚'
			html = etree.HTML(result)
			tag_list = html.xpath('//*[@id="selTag"]/div/a/text()')
			#print(tag_list)
			if '全部' in tag_list:
				tag_list.remove('全部')
			for x in tag_list:
				if last_stop:
					resume_at = tag_list.index(last_stop)
				else:
					resume_at = 1
				if tag_list.index(x) >= resume_at:
					for y in range(1, 26):
						url = base_url + '?period={0}&tag={1}&page={2}'.format(period, x, str(y))
						print('当前tag, period,tag,page:{},{},{},{}'.format(tag, period, x, str(y)))
						result = requests.get(url, headers=self.headers).text
						try:
							result = json.loads(result)
							if result['msg'] == '没有更多内容':
								print('该页没有更多内容')
								break
							if result['Message'] == '哎呦，访问太频繁了，请稍后再试':
								print('被拦截了')
						except:
							pass
						self.parse_feigua_ids(result, y)

	def parse_feigua_ids(self, data, page):
		html = etree.HTML(data)
		if page == 1:
			tr_list = html.xpath('//*[@id="js-blogger-container"]/tr')
			for tr in tr_list:
				url_params = tr.xpath('./td[last()]/a/@href')[0]
				feigua_user_id = re.match('.*?id=(.*?)&.*', url_params, re.S).group(1)
				self.save_users(feigua_user_id)
		else:
			tr_list = html.xpath('//tr')
			for tr in tr_list:
				last_td = etree.tostring(tr.xpath('./td[last()]')[0], encoding="utf-8")
				feigua_user_id = re.match('.*?id=(.*?)&.*', last_td.decode('utf-8'), re.S).group(1)
				#print(feigua_user_id)
				self.save_users(feigua_user_id)

	def get_awemes(self): #{"Status":429,"Message":"哎呦，访问太频繁了，请稍后再试"}
		user_list = self.get_users()
		print('共有user：' + str(len(user_list)))
		for user in user_list:
			url = 'https://dy.feigua.cn/Blogger/AwemeList?id='+ user +'&page=1&sort=1'
			result = requests.get(url, headers=self.headers).text
			try:
				result = json.loads(result)
				if result['Message'] == '哎呦，访问太频繁了，请稍后再试':
					print('被拦截了')
					break
			except:
				pass
			html = etree.HTML(result)
			tr_list = html.xpath('//*[@id="js-blogger-history-awemes"]/tr')
			aweme_id = None
			for tr in tr_list:
				try:
					a_div = tr.xpath('./td[1]/div[@class="media-list"]/div[@class="item-media"]/a[1]')[0]
					if not 'no-video' in a_div.xpath('./img/@src')[0]:
						aweme_id = tr.xpath('./td[1]/div[@class="media-list"]/div[@class="item-media"]/a[1]/@data-awemeid')[0]
						break
				except:
					pass
			if aweme_id:
				#print(aweme_id)
				self.save_aweme(aweme_id)
				self.delete_users(user)
			else:
				print('未获得aweme_id，feigua_user_id:' + user)

	def save_users(self, feigua_user_id):
		if not self.db1.sismember(self.key4, feigua_user_id):
			self.db1.sadd(self.key1, feigua_user_id)
			self.db1.sadd(self.key4, feigua_user_id)

	def get_users(self):
		return list(self.db1.smembers(self.key1))

	def delete_users(self, feigua_user_id):
		self.db1.srem(self.key1, feigua_user_id)

	def back_up_users(self):
		users = self.get_users()
		print(len(users))
		for user in users:
			self.db1.sadd(self.key4, user)
			print(user)

	def save_aweme(self, feigua_aweme_id):
		self.db1.sadd(self.key2, feigua_aweme_id)	

if __name__ == '__main__':
	get_feigua = GetFeigua()
	get_feigua.get_feigua_ids()
	#get_feigua.get_awemes()

#url = 'https://dy.feigua.cn/Rank/Tag?period=month&tag=%E7%BD%91%E7%BA%A2%E7%BE%8E%E5%A5%B3&keyword=&datecode=202004&page=25'
#url = 'https://dy.feigua.cn/Blogger/Detail?id=1916&timestamp=1589790650&signature=83fc67e3e1153b9e525fe98790001e84'
#url = 'https://dy.feigua.cn/Blogger/FansAnalysis?uid=24058267831'
#url = 'https://dy.feigua.cn/Blogger/AwemeList?id=1916&page=1&sort=1'
#url = 'https://dy.feigua.cn/Rank/Tag'
#url = 'https://dy.feigua.cn/Blogger/Detail?id=6204564&timestamp=1590057349&signature=ff32a42aee92cbd0ca05cef7994ae7ea'
#url = 'https://dy.feigua.cn/Rank/Area'
#url = 'https://dy.feigua.cn/Blogger/AwemeList?id=1189&page=1&sort=1'
