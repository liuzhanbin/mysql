import paramiko
ip1='192.168.1.102'
ip2='192.168.1.102'
dirname1='/opt/test1'
dirname2='/opt/test2'

diff=0

ssh1 = paramiko.SSHClient()
ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh1.connect(hostname=ip1, port=22, username='root')

ssh2 = paramiko.SSHClient()
ssh2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh2.connect(hostname=ip2, port=22, username='root')

#stdin, stdout, stderr = ssh.exec_command('md5sum /opt/md5/md5.txt')
#print(stdout.readlines())

sftp1=ssh1.open_sftp()
sftp2=ssh2.open_sftp()


filename1=sorted(sftp1.listdir("%s" % dirname1))
filename2=sorted(sftp2.listdir("%s" % dirname2))
#sort=sorted(filename1)
#print(sort)
if filename1==filename2:
    print("------------")
    print("info:%s 目录 %s 和 %s 目录 %s 包含文件名相同,包含文件:%s" % (ip1,dirname1,ip2,dirname2,filename1))
    print("--")
    #print("filename1 is %s" % filename1)
    #print("filename2 is %s" % filename2)
    dict1 = {}
    dict2 = {}
    for file1 in filename1:
        #print(file1)
        stdin, stdout, stderr = ssh1.exec_command('md5sum %s/%s' % (dirname1, file1))
        md1 = stdout.readlines()[0].split(' ')[0]
        # print(md1)
        dict1[file1] = md1
    #print(dict1)

    for file2 in filename2:
     #   print(file2)
        stdin, stdout, stderr = ssh2.exec_command('md5sum %s/%s' % (dirname2, file2))
        md2 = stdout.readlines()[0].split(' ')[0]
        # print(md1)
        dict2[file2] = md2
    #print(dict2)

    for file in filename1:
        if dict1[file] == dict2[file]:
            print("md5值相等数据一致。%s:%s/%s; %s:%s/%s " % (ip1,dirname1,file,ip2,dirname2,file))
            print("--")
            pass
        else:
            print("--!!!!!!!!!!!!!!!--")
            print("--!md5值不等,数据不一致 %s:%s/%s; %s:%s/%s " % (ip1, dirname1, file, ip2, dirname2, file))
            print("--!!!!!!!!!!!!!!!--")
            diff=1
            #print("!!!md5值不等,数据不一致!!! ip1 is %s,文件1:%s/%s,md5值为%s; ip2 is %s,文件2:%s/%s,md5值为%s" % (ip1,dirname1,file, dict1[file],ip2,dirname2,file, dict2[file]))
else:
    only_exist1=set(filename1)-set(filename2)
    only_exist2 = set(filename2) - set(filename1)
    print("两个目录包含的文件不一致!!!!")
    if only_exist1==set():
        print("只存在 %s:%s 中的为%s" % (ip2, dirname2,only_exist2))
    if only_exist1!=set():
        print("只存在 %s:%s 中的为%s" % (ip1, dirname1,only_exist1))
    if only_exist2==set():
        print("只存在 %s:%s 中的为%s" % (ip1, dirname1,only_exist1))
    if only_exist2!=set():
        print("只存在 %s:%s 中的为%s" % (ip2, dirname2,only_exist2))
        #print(len(only_exist1))
        #print(len(only_exist2))

        #print("%s 只存在 %s:%s 中" % (only_exist1, ip1, dirname1))

        #print("ip1 is %s,filename1 is %s/%s" % (ip1,dirname1,filename1))
    #print("ip2 is %s,filename2 is %s/%s" % (ip2,dirname2,filename2))
if diff==0:
    print("文件全部一致")
#print(diff)
ssh1.close()
ssh2.close()