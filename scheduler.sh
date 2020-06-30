

# get_rank_list.py，1小时跑一次
* */1 * * * Path='/data/data/com.termux/files/usr/bin/bash' /data/data/com.termux/files/home/schedule/get_rank_list_main.sh >> /data/data/com.termux/files/home/schedule/log/get_rank_list_main_`date "+%Y%m%d"`.log 2>&1

cat << 'eof' > /data/data/com.termux/files/home/schedule/get_rank_list_main.sh
# test_main.sh
prc_name="get_rank_list.py"
work_path="/data/data/com.termux/files/home/douyin"

if [ `ps -ef|grep ${prc_name}|grep -v grep|wc -l` -gt 0 ] ;then
ps -ef | grep ${prc_name} | grep -v grep | awk '{print $2}' | xargs kill -9
fi
python -u ${work_path}/${prc_name}  &
eof

chmod 777 /data/data/com.termux/files/home/schedule/get_rank_list_main.sh

#get_lives.py，1小时跑一次
cat << 'eof' > /data/data/com.termux/files/home/schedule/get_lives_main.sh
# test_main.sh
prc_name="get_lives.py"
work_path="/data/data/com.termux/files/home/douyin"

if [ `ps -ef|grep ${prc_name}|grep -v grep|wc -l` -gt 0 ] ;then
ps -ef | grep ${prc_name} | grep -v grep | awk '{print $2}' | xargs kill -9
fi
python -u ${work_path}/${prc_name}  &
eof

chmod 777 /data/data/com.termux/files/home/schedule/get_lives_main.sh

* */1 * * * Path='/data/data/com.termux/files/usr/bin/bash' /data/data/com.termux/files/home/schedule/get_lives_main.sh >> /data/data/com.termux/files/home/schedule/log/get_lives_main_`date "+%Y%m%d"`.log 2>&1


#get_item_lists.py，2小时跑一次
cat << 'eof' > /data/data/com.termux/files/home/schedule/get_item_lists_main.sh
# test_main.sh
prc_name="get_item_lists.py"
work_path="/data/data/com.termux/files/home/douyin"

if [ `ps -ef|grep ${prc_name}|grep -v grep|wc -l` -gt 0 ] ;then
ps -ef | grep ${prc_name} | grep -v grep | awk '{print $2}' | xargs kill -9
fi
python -u ${work_path}/${prc_name}  &
eof

chmod 777 /data/data/com.termux/files/home/schedule/get_item_lists_main.sh

* */2 * * * Path='/data/data/com.termux/files/usr/bin/bash' /data/data/com.termux/files/home/schedule/get_item_lists_main.sh >> /data/data/com.termux/files/home/schedule/log/get_item_lists_main_`date "+%Y%m%d"`.log 2>&1

#get_items.py，2小时跑一次
cat << 'eof' > /data/data/com.termux/files/home/schedule/get_items_main.sh
# test_main.sh
prc_name="get_items.py"
work_path="/data/data/com.termux/files/home/douyin"

if [ `ps -ef|grep ${prc_name}|grep -v grep|wc -l` -gt 0 ] ;then
ps -ef | grep ${prc_name} | grep -v grep | awk '{print $2}' | xargs kill -9
fi
python -u ${work_path}/${prc_name}  &
eof

chmod 777 /data/data/com.termux/files/home/schedule/get_items_main.sh

* */2 * * * Path='/data/data/com.termux/files/usr/bin/bash' /data/data/com.termux/files/home/schedule/get_items_main.sh >> /data/data/com.termux/files/home/schedule/log/get_items_main_`date "+%Y%m%d"`.log 2>&1
