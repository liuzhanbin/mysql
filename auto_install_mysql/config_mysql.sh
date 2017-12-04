#!/usr/bin/env bash
master_ip=`cat ./hosts|grep master|awk -F " " '{print $2}'|awk -F "=" '{print$2}'`
#echo $master_ip
for slave_ip in `cat ./hosts|grep slave|awk -F " " '{print $2}'|awk -F "=" '{print$2}'`;do
echo $slave_ip
done