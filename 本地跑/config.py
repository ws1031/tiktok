#获取器
#ID = "MT005"

#log
LOGPATH = 'C:\\Users\\百芯科技\\scraping\\douyin6\\logs'
#LOGPATH = '/data/data/com.termux/files/home/douyin/logs'
LOGSIZE = 1024*1024*3
FILE_DIRECTORY = 'data_files'

#redis
RHOST = 'r-bp1758aa6549c324pd.redis.rds.aliyuncs.com'
RPORT = 13457
RPASSWORD = 'U78afbZtttT678'

RHOST2 = 'r-bp1db51661f4d0e4pd.redis.rds.aliyuncs.com'
RPORT2 = 13457
RPASSWORD2 = 'U78afbZtttT678'

#mysql
MHOST = '47.114.166.130'
MPORT = 13306
MUSER = 'bxusr'
MPASSWORD = 'bxdb@TT12'
MDB = 'bxdb'

#alarm
ERRORSDICT = {'1': '请求反复被拦截', '2': '反复连接失败', '3': 'mysql反复入库失败', '4': 'redis反复获取或存储数据失败'}
MODULESDICT = {'1': 'get_raw_data.py', '2': 'get_new_users.py', '3': 'check_users.py', '4': 'get_lives.py', '5': 'get_items.py', '6': 'mysql_client.py'}
WORKERSDICT = {'01':'MT001', '02':'MT002', '03':'MT003', '04':'MT004', '05':'MT005', '06':'MT006', '07':'MT007', '08':'MT008'}