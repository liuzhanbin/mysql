#===============================
#每天一次增量备份：除了周一凌晨0点
#备份目录形式：IP_MySQL实例端口号/年份周数，比如：192.168.40.160_3306/201718
#0 0 * * 0,2-6 sh /usr/local/dba/db_backup_day_00.sh &>> /usr/local/dba/log/incre_bak_3306.log
#===============================


monitor_host="172.16.33.209"
backup_type="xtrabackup"
port=__port__
ip=__backupip__
host_name=$(hostname)
host_ip="${ip}_${port}"
backup_dir="/backup/mysql/${host_ip}"
data_dir=${backup_dir}/data
tmp_dir=${backup_dir}/tmp
week_dir="${backup_dir}/$(date +"%Y%W")"
inc_backup_dir="inc_day_$(date +"%Y%W_%Y%m%d_%H")"
my_cnf="__mysql_path__/${port}/conf/my.cnf"
user='bkpuser'
password=''
slave_workers=`mysql -h127.0.0.1 -P$port -u$user -p$password -BNe "show variables like 'slave_parallel_workers';" 2> /dev/null|awk -F " " '{print $2}'`
to_mail=
subject="增量备份状态:"
content="来自${host_name}:${host_ip} 增量备份状态:"

if [ ! -d $week_dir ]
then
    echo "$week_dir 全量备份不存在！"
  	exit 1
fi

rm -f $tmp_dir/* > /dev/null
rm -f $data_dir/* > /dev/null



filename=${week_dir}/${inc_backup_dir}
rm -rf ${filename} > /dev/null

cur_date=$(date +"%Y-%m-%d")
start_time=$(date +"%Y-%m-%d %H:%M:%S")
mysql -h$monitor_host -udba -ppass dba_monitor --port=3306  <<EOF
replace into dbback_list
(host_name,host_ip,backup_to,backup_status,backup_type,curdate,backup_st_time)
VALUES('${host_name}','${host_ip}','${filename}','running','${backup_type}','${cur_date}','${start_time}');
EOF

mysql -h127.0.0.1 -P$port -u$user -p$password -e "set global slave_parallel_workers = 0;stop slave;start slave;"

/usr/local/percona-xtrabackup-2.4.5-Linux-x86_64/bin/innobackupex --defaults-file=$my_cnf --host=127.0.0.1 --port=$port --tmpdir=$tmp_dir --user=$user --password=$password --slave-info --no-timestamp --history=inc_day_backup --incremental-history-name=full_backup  --incremental ${filename}
status=$?
end_time=$(date +"%Y-%m-%d %H:%M:%S")
mysql -h127.0.0.1 -P$port -u$user -p$password -e "set global slave_parallel_workers = ${slave_workers};stop slave;start slave;"


if [[ $status -eq 0 ]]; then
    status='ok'
    cd ${week_dir}
    tar cvf - ${inc_backup_dir} | pigz > ${inc_backup_dir}.tar.gz
    rm -rf ${inc_backup_dir} > /dev/null
    sleep 1
    filesize=$(ls -lh ${filename}.tar.gz|awk -F " " '{print $5}')
else
    status='fail'
    filesize=''
fi


#sleep 1
#filesize=$(du -sh ${inc_backup_dir}.tar.gz |awk '{print $1}')

#需在 ${monitor_host} 上跑4000端口的邮件服务。
curl http://${monitor_host}:4000/sender/mail -d "tos=${to_mail}&subject=${subject} ${status}&content=${content} ${status} ${filesize}"

mysql -h$monitor_host -udba -ppass dba_monitor --port=3306  <<EOF
update dbback_list set backup_status='${status}',backup_en_time='${end_time}',filesize='${filesize}' where host_ip='${host_ip}' and curdate='${cur_date}';
EOF