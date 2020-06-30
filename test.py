# -*- coding: utf-8 -*-

import gevent
import gevent.monkey
gevent.monkey.patch_all()


import json
import pymysql
import requests
import asyncio
import aiomysql
import csv
import codecs
import xlrd
import xlwt
import re
from xlutils.copy import copy

from get_raw_data import GetRawData
from redis_client import RedisClient
from mysql_client import MysqlClient
from config import STUPID_KEY_WORDS
from config import FILE_DIRECTORY
from logger import logger

class SaveLiveUsers():
	def __init__(self):
		self.get_raw_data = GetRawData()
		#self.db = pymysql.connect(host='47.114.166.130', port=13306, user='bxusr', password='bxdb@TT12', db='bxdb', charset='utf8mb4')
		#self.cursor = self.db.cursor()
		self.db = pymysql.connect(host='localhost', port=3306, user='root', password='sxy199311', db='bxmind', charset='utf8mb4')
		self.cursor = self.db.cursor()
		self.mysql_client = MysqlClient()
		self.redis_client = RedisClient()
		self.stupid_key_words = STUPID_KEY_WORDS
		self.a_list = []
		self.b_list = []

	def into_mysql(self, data, table):
		keys = ','.join(data.keys())
		values = ','.join(['%s'] * len(data))	
		sql = 'insert into %s (%s) values (%s)' %(table, keys, values)
		try:
			self.cursor.execute(sql, tuple(data.values()))
			self.db.commit()
		except Exception as e:
			print(e.args)

	def is_qualified(self, nickname):
		for word in self.stupid_key_words:
			if word in nickname:
				return False
		return True

	def run_a(self):
		table = 'dy_live_lives'
		with open('lives_20200614.txt', 'r', encoding='utf-8') as f:
			lines = f.readlines()
			for line in lines:
				#print(line)

				data = json.loads(line)
				nickname = data.get('nickname')
				sec_user_id = data.get('sec_user_id')
				if data.get('status') == 4:
					if self.is_qualified(nickname):
						self.into_mysql(data, table)
					else:
						self.redis_client.delete_users(sec_user_id)
						self.redis_client.delete_live_users(sec_user_id)

	def replicate_table(self):
		sql = 'CREATE TABLE dy_sample LIKE dy_live_lives'
		self.cursor.execute(sql)

	def select_users(self):
		sql = 'SELECT room_id, sec_user_id, nickname, short_id, total_viewer, like_count, follower_count, signature, city FROM dy_live_lives WHERE total_viewer > 50000 AND follower_count > 500000'
		self.cursor.execute(sql)
		row = self.cursor.fetchone()
		while row:
			data = {}
			data['room_id'] = row[0]
			data['sec_user_id'] = row[1]
			data['nickname'] = row[2]
			data['short_id'] = row[3]
			data['total_viewer'] = row[4]
			data['like_count'] = row[5]
			data['follower_count'] = row[6]
			data['signature'] = row[7]
			data['city'] = row[8]
			self.a_list.append(data)
			row = self.cursor.fetchone()

	def get_cates(self, data):
		sec_user_id = data['sec_user_id']
		try:
			cates_raw_data = self.get_raw_data.get_cates(sec_user_id)
		except Exception as e:
			logger.error('get_cates出错-' + e.args[0] + '-sec_user_id-' + sec_user_id)
			return None
		cate_list = cates_raw_data.get('user_shop_categories')
		for each in cate_list:
			cate = each['name']
			number = each['count']
			if cate in ['零食', '食品', '花茶', '果茶'] and number >= 3:
				self.b_list.append(data)
				break

	def run_b(self):
		self.select_users()
		logger.info('a_list共有数据-' + str(len(self.a_list)))

		batch_size = 100 
		for batch_limit in range(0, len(self.a_list), batch_size):
			start = batch_limit
			stop = min(batch_limit+batch_size, len(self.a_list))
			logger.info('当前爬取用户序号-' + str(start+1) + '-' + str(stop))
			tasks = [gevent.spawn(self.get_cates, data) for data in self.a_list[start:stop]]
			gevent.joinall(tasks)

		logger.info('b_list共有数据-' + str(len(self.b_list)))
		for data in self.b_list:
			self.into_mysql(data, 'dy_sample')

	def run_c(self):
		self.select_users()
		for data in self.a_list:
			self.into_mysql(data, 'dy_sample')

	def select_rooms(self):
		room_list = []
		sql = 'SELECT room_id FROM dy_sample'
		self.cursor.execute(sql)
		row = self.cursor.fetchone()
		while row:
			room_list.append(row[0])
			row = self.cursor.fetchone()
		return room_list

	def get_txt(self):
		with open('lives_20200605.txt', 'r', encoding='utf-8') as f:
			lines = f.readlines()
			for line in lines:
				print(line)
				break

	def write_to_file(self, item_list):
		today = time.strftime('%Y-%m-%d', time.localtime())
		today = today.replace('-', '')
		with open (FILE_DIRECTORY + '/' + 'item_lists_sample'+ '_' + today + '.txt', 'a', encoding='utf-8') as file:
			file.write(item_list + '\n')

	def run_d(self):
		url = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=606547898363&sellerId=2206709156233&modules=dynStock,qrcode,viewer,price,duty,xmpPromotion,delivery,activity,fqg,zjys,couponActivity,soldQuantity,page,originalPrice,tradeContract&callback=onSibRequestSuccess'

		headers = {
			'Referer': 'https://item.taobao.com/item.htm?id=606547898363',
			'Sec-Fetch-Mode': 'no-cors',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
		}
		response = requests.get(url, headers=headers, allow_redirects=False)
		print(response.text)

	def run_e(self):
		file = 'lives_20200609.txt'
		table = 'dy_live_lives'
		data_batch = []
		batch_size = 200

		loop = asyncio.get_event_loop()
		task = loop.create_task(self.mysql_client.connect_mysql(loop))
		loop.run_until_complete(task)

		with open(file, 'r', encoding='utf-8') as f:
			lines = f.readlines()
			for line in lines:
				line = json.loads(line)
				if self.is_qualified(line.get('nickname')):
					if line.get('status') == 4:
						data_batch.append(line) #最初数据没有入库然后程序很快就结束，是因为，4写成了’4‘。然后我以为其他地方有问题，就去打印，然后由于颜文字，打印出错（颜文字不会给入库造成错误），就在颜文字上卡了很久#最初数据没有入库然后程序很快就结束，是因为，4写成了’4‘。然后我以为其他地方有问题，就去打印，然后由于颜文字，打印出错（颜文字不会给入库造成错误），就在颜文字上卡了很久
						line.pop('mobile')
					if len(data_batch) >= batch_size: 
						tasks = [self.mysql_client.into_mysql(loop, i, table) for i in data_batch]
						loop.run_until_complete(asyncio.wait(tasks))
						#tasks = [gevent.spawn(self.into_mysql, line) for line in data_batch]
						#gevent.joinall(tasks)
						data_batch.clear()
				else:
					self.redis_client.delete_users(line.get('sec_user_id'))
					self.redis_client.delete_live_users(line.get('sec_user_id'))
					print('删除user', line.get('nickname'))

	def run_f(self):
		file_a = 'lives_20200623.txt'
		file_b = '第四批_抖音主播_去重前.csv'
		with open(file_a, 'r', encoding='utf-8') as f:
			with open(file_b, 'a', encoding='utf-8-sig', newline='') as g:
				lines = f.readlines()
				first_line = json.loads(lines[0])
				first_line.pop('mobile')
				keys = list(first_line.keys())
				writer = csv.DictWriter(g, fieldnames = keys) 
				for line in lines:
					line = json.loads(line)
					if self.is_qualified(line.get('nickname')):
						if line.get('status') == 4:
							line.pop('mobile')
							writer.writerow(line)

	def run_g(self):
		read_workbook = xlrd.open_workbook('C:/Users/百芯科技/scraping/douyin7/第四批_抖音主播_去重后.xlsx')
		write_workbook = copy(read_workbook)
		read_sheet = read_workbook.sheet_by_name('Sheet1')
		write_sheet = write_workbook.get_sheet(0)

		nrows = read_sheet.nrows
		ncolumns = read_sheet.ncols
		for row in range(1, nrows):
			text = read_sheet.row(row)[15].value
			if text:
				data = re.match('.*(1\d{10}).*', str(text), re.S)
				if data:
					mobile = data.group(1)
					write_sheet.write(row, ncolumns, mobile)
		write_workbook.save('C:/Users/百芯科技/scraping/douyin7/第四批_抖音主播_去重后_电话.xlsx')


if __name__ == '__main__':
	save_live_users = SaveLiveUsers()
	save_live_users.run_g()