#获取器
#ID = "MT005"

#log
LOGPATH = 'C:\\Users\\百芯科技\\scraping\\douyin7\\logs'
#LOGPATH = '/data/data/com.termux/files/home/douyin/logs'
LOGSIZE = 1024*1024*1
FILE_DIRECTORY = 'data_files'
#FILE_DIRECTORY = '/data/data/com.termux/files/home/douyin/data_files'

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

#constants
STUPID_KEY_WORDS = ['公司', '店', '铺', '厂', '工', '产', '行', '鞋', '装', '价', '市', '县', '区', '服', '饰', '商', '贸', '牌', '汇', '潮', '馆', '裤', '业', '专', '卖', '时尚', '品', '妆', '玩具', '语文', '数学', '语', '科学', '物理', '化学', '生物', '政治', '历史', '地理', '官方', '殖','宠物', '户外', '少儿', '教', '课', '坊', '海鲜', '车', '学', '旅游', '剪', '制', '电影', '机', '口才', '拍', '书', '字', '榜', '音乐', '手工', '思维', '咨', '球', '琴', '州', '针织', '说', '水果', '园', '讲', '考', '动画', '情感', '星座', '销售', '心理', '段子', '瑜伽', '老师', '舞', '游戏', '鲜花', '萌宠', '大码', '珠宝', '翡翠', '吉他', '乐器', '零食', '绘画', '科技', '武术', '中医']


#alarm
ERRORSDICT = {'1': '请求反复被拦截', '2': '反复连接失败', '3': 'mysql反复入库失败', '4': 'redis反复获取或存储数据失败'}
MODULESDICT = {'1': 'get_raw_data.py', '2': 'get_new_users.py', '3': 'check_users.py', '4': 'get_lives.py', '5': 'get_items.py', '6': 'mysql_client.py'}
WORKERSDICT = {'01':'MT001', '02':'MT002', '03':'MT003', '04':'MT004', '05':'MT005', '06':'MT006', '07':'MT007', '08':'MT008'}

PARAMS = [{"device_type":"MI%206","uuid":"863254012409123","iid":"111280011708","cdid":"7526ed37-f767-480d-8ef0-0bd54f0a9813","openudid":"2405bd8d333e9536", "device_id":"70361550255"},
{"device_type":"MI%206","uuid":"355757011409121","iid":"1714882541260359","cdid":"7b1d77edd-7acb-46d6-b8eb-8bc9fb42f5f4","openudid":"1405bd8d333e9800", "device_id":"71250592861"},
{"device_type":"google%20Pixel%202","uuid":"865166010409129","iid":"2647268807942983","cdid":"98d08554-401d-44e6-8280-4aaeeecf9f8a","openudid":"405bd8d333e99001", "device_id":"4300934295592167"},
{"device_type":"HUAWEI%20MLA-AL10","uuid":"863064010409128","iid":"111286720559","cdid":"51198fde-114c-4cb1-80ee-6905f6c4174c","openudid":"405bd8d333e94280", "device_id":"71315245001"},
{"device_type":"SM-G955F","uuid":"355757010409122","iid":"2172274732445896","cdid":"baec6b4b-630e-47ed-ae00-3895a21c072d","openudid":"405bd8d333e94150", "device_id":"69943155325"}]