import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ip1='192.168.1.102'
dirname1='/opt/test1'
dirname2='/opt/test2'

ssh.connect(hostname=ip1, port=22, username='root')

#stdin, stdout, stderr = ssh.exec_command('md5sum /opt/md5/md5.txt')
#print(stdout.readlines())

sftp=ssh.open_sftp()



filename1=sftp.listdir("%s" % dirname1)
filename2=sftp.listdir("%s" % dirname2)
if filename1==filename2:
    print("OK OK OK")
    print("filename1 is %s" % filename1)
    print("filename2 is %s" % filename2)
    dict1 = {}
    dict2 = {}
    for file1 in filename1:
        #print(file1)
        stdin, stdout, stderr = ssh.exec_command('md5sum %s/%s' % (dirname1, file1))
        md1 = stdout.readlines()[0].split(' ')[0]
        # print(md1)
        dict1[file1] = md1
    #print(dict1)

    for file2 in filename2:
     #   print(file2)
        stdin, stdout, stderr = ssh.exec_command('md5sum %s/%s' % (dirname2, file2))
        md2 = stdout.readlines()[0].split(' ')[0]
        # print(md1)
        dict2[file2] = md2
    #print(dict2)

    for file in filename1:
        if dict1[file] == dict2[file]:
            print("----------")
            print("md5 值相等数据一致。 文件1:%s/%s; 文件2%s/%s ,md5值为%s" % (dirname1,file,dirname2,file, dict1[file]))
        else:
            #print("no")
            print("----------")
            print("!!!md5值不等,数据不一致!!! 文件1:%s/%s,md5值为%s; 文件2:%s/%s,md5值为%s" % (dirname1,file, dict1[file],dirname2,file, dict2[file]))
else:
    print("NOT OK!!!!")
    print("filename1 is %s" % filename1)
    print("filename2 is %s" % filename2)


