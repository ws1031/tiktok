import time
import pymysql
import aiomysql
import re

class MysqlClient():
	def __init__(self):
		self.pool = None

	async def connect_mysql(self, loop):
		if self.pool == None:
			self.pool = await aiomysql.create_pool(host='47.114.166.130', port=13306, user='bxusr', password='bxdb@TT12', db='bxdb', loop=loop, charset='utf8mb4', autocommit=True)
			return self.pool
		else:
			return self.pool

	async def into_mysql(self, loop, data, table): #这个是直播入库使用的，into_mysql_2是商品入库使用的
		pool = await self.connect_mysql(loop)
		async with self.pool.acquire() as db:
			async with db.cursor() as cursor:

				keys = ','.join(data.keys())
				values = ','.join(['%s'] * len(data))	
				sql = 'insert into %s (%s) values (%s)' %(table, keys, values)

				try:
					await cursor.execute(sql, tuple(data.values()))
					await db.commit()
				except aiomysql.Error as e:
					print('直播入库失败。' + str(e.args[0]) + '-' + e.args[1])