# -*- coding: utf-8 -*-
import oss2
import sys

class Oss():
	def __init__(self):
		self.access_key_id = 'LTAI4FqZ17cgQCPLWCudzjN9'
		self.access_key_secret = 'UbnMJLm52oqHIBIZyvXGPx4apkIehS'
		self.end_point = 'http://oss-cn-hangzhou.aliyuncs.com'
		self.bucket_name = 'mitao-itmlogo'
		self.auth = oss2.Auth(self.access_key_id, self.access_key_secret)
		self.bucket = oss2.Bucket(self.auth, self.end_point, self.bucket_name)

	def put_file(self, object_name, local_file):
		self.bucket.put_object_from_file(object_name, local_file)

	def get_file(self, object_name, local_file):
		self.bucket.get_object_to_file(object_name, local_file)

if __name__ == '__main__':
	oss = Oss()

	try:
		object_name = sys.argv[1]
	except IndexError:
		object_name = input('请指定oos中带有后缀在内的文件名:')

	try:
		local_file = sys.argv[2]
	except IndexError:
		local_file = input('请指定本地带有文件后缀在内的完整路径：')

	try:
		task = sys.argv[3]
	except IndexError:
		task = input('上传文件请输入put，下载文件请输入get：')

	if task == 'get':
		oss .get_file(object_name, local_file)
	elif task == 'put':
		oss.put_file(object_name, local_file)
	else:
		print('上传文件请输入put，下载文件请输入get，您输入的既不是put也不是get。')