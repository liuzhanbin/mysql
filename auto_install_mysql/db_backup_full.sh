#===============================
#每周一次全量备份：每周1凌晨0点开始备份
#0 0 * * 1 sh /usr/local/dba/db_backup_full.sh &>> /usr/local/dba/log/full_bak_3306.log
#备份目录形式：IP_MySQL实例端口号/年份周数，比如：192.168.40.160_3306/201718
#===============================



monitor_host="192.168.40.65"
backup_type="xtrabackup"
port=__port__
ip=__backupip__
host_name=$(hostname)
host_ip="${ip}_${port}"
backup_dir="/backup/mysql/${host_ip}"
data_dir=${backup_dir}/data
tmp_dir=${backup_dir}/tmp
week_dir="${backup_dir}/$(date +"%Y%W")"
my_cnf="__mysql_path__/${port}/conf/my.cnf"
user='bkpuser'
password=''
slave_workers=10
to_mail=
subject="全量备份状态:"
content="来自${host_name}:${host_ip} 全量备份状态:"

rm -f $tmp_dir/* > /dev/null
rm -f $data_dir/* > /dev/null

if [ ! -d $data_dir ]
then
    mkdir -p $data_dir
    chmod -R 755 $data_dir
fi

if [ ! -d $tmp_dir ]
then
    mkdir -p $tmp_dir
    chmod -R 755 $tmp_dir
fi

if [ ! -d $week_dir ]
then
    mkdir -p $week_dir
    chmod -R 755 $week_dir
fi

filename=${week_dir}/full_$(date +"%Y%W").tar.gz
cur_date=$(date +"%Y-%m-%d")
start_time=$(date +"%Y-%m-%d %H:%M:%S")
mysql -h$monitor_host -udba -ppass dba_monitor --port=3306  <<EOF
replace into dbback_list
(host_name,host_ip,backup_to,backup_status,backup_type,curdate,backup_st_time)
VALUES('${host_name}','${host_ip}','${filename}','running','${backup_type}','${cur_date}','${start_time}');
EOF

mysql -h127.0.0.1 -P$port -u$user -p$password -e "set global slave_parallel_workers = 0;stop slave;start slave;"

/usr/local/percona-xtrabackup-2.4.5-Linux-x86_64/bin/innobackupex --defaults-file=$my_cnf --host=127.0.0.1 --port=$port  --tmpdir=$tmp_dir --user=$user --password=$password --slave-info --no-timestamp  --history=full_backup --stream=tar ${data_dir}  | pigz -p 16 > ${filename}
status=$?
end_time=$(date +"%Y-%m-%d %H:%M:%S")

mysql -h127.0.0.1 -P$port -u$user -p$password -e "set global slave_parallel_workers = ${slave_workers};stop slave;start slave;"


if [[ $status -eq 0 ]]; then
    status='ok'
    sleep 1
    filesize=$(du -sh ${filename} |awk '{print $1}')
else
    status='fail'
    filesize=''
fi


curl http://192.168.40.65:4000/sender/mail -d "tos=${to_mail}&subject=${subject} ${status}&content=${content} ${status} ${filesize}"

mysql -h$monitor_host -udba -ppass dba_monitor --port=3306  <<EOF
update dbback_list set backup_status='${status}',backup_en_time='${end_time}',filesize='${filesize}' where host_ip='${host_ip}' and curdate='${cur_date}';
EOF