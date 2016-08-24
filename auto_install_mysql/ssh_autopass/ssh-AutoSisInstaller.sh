#!/bin/bash
#First on the server install the sshpass
#wget http://nchc.dl.sourceforge.net/sourceforge/sshpass/sshpass-1.04.tar.gz
yum -y install gcc
tar xvf sshpass-1.04.tar.gz
cd sshpass-1.04
./configure --prefix=/usr/local/sshpass
make && make install
echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
cd ../
rm -rf sshpass-1.04

hosts=`cat ./ip_pass.txt |sed '/^#/d'|sed '/^$/d'|awk '{print $1}'`
for host in $hosts
do 
ping -c 2 -W 2 $host &> /dev/null
if [ $? = 0 ]
then
passwd=`awk /$host/'{print $2}' ./ip_pass.txt`
passdir="/usr/local/sshpass/bin"
${passdir}/sshpass -p "${passwd}" ssh-copy-id -i ${host} 
else
echo "${host} unreacheable!!!"
fi
done
