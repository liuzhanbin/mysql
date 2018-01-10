import re
import pymysql
import time
from multiprocessing import Process
import email
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime

now_time = datetime.datetime.now()
yes_time=now_time + datetime.timedelta(days=-1)
yes_time_nyr=str(yes_time.strftime('%Y-%m-%d'))
first_seen_set=str(yes_time_nyr.__add__(' 00:00:00'))
last_seen_set=str(time.strftime('%Y-%m-%d 00:00:00'))
#print(first_seen_set,last_seen_set)
def replaceAll(old, new, str):
    while str.find(old) > -1:
        str = str.replace(old, new)
    return str

class MailSender(object):
    def __init__(self):
        try:
            self.MAIL_REVIEW_SMTP_SERVER = 'mail.maillists.tongbanjie.org'
            self.MAIL_REVIEW_SMTP_PORT = 25
            self.MAIL_REVIEW_FROM_ADDR = 'DB_monitor@mail.maillists.tongbanjie.org'
            self.MAIL_REVIEW_FROM_PASSWORD = 'tbj2018!X'

            self.MAIL_REVIEW_DBA_ADDR =''
            self.MAIL_REVIEW_SMTP_TLS =False

        except AttributeError as a:
            print("Error: %s" % a)
        except ValueError as v:
            print("Error: %s" % v)

    def _format_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    def _send(self, strTitle, strContent, listToAddr):
        msg = MIMEText(strContent, 'plain', 'utf-8')
        # 收件人地址:

        msg['From'] = self._format_addr(self.MAIL_REVIEW_FROM_ADDR)
        #msg['To'] = self._format_addr(listToAddr)
        msg['To'] = ','.join(listToAddr)
        msg['Subject'] = Header(strTitle, "utf-8").encode()

        server = smtplib.SMTP(self.MAIL_REVIEW_SMTP_SERVER, self.MAIL_REVIEW_SMTP_PORT)  # SMTP协议默认端口是25
        #server.set_debuglevel(1)
        if self.MAIL_REVIEW_SMTP_TLS:
            server.starttls()

        #如果提供的密码为空，则不需要登录SMTP server
        if self.MAIL_REVIEW_FROM_PASSWORD != '':
            server.login(self.MAIL_REVIEW_FROM_ADDR, self.MAIL_REVIEW_FROM_PASSWORD)
        sendcontent = server.sendmail(self.MAIL_REVIEW_FROM_ADDR, listToAddr, msg.as_string())
        server.quit()

    #调用方应该调用此方法，采用子进程方式异步阻塞地发送邮件，避免邮件服务挂掉影响archer主服务
    def sendEmail(self, strTitle, strContent, listToAddr):
        p = Process(target=self._send, args=(strTitle, strContent, listToAddr))
        p.start()


conn=pymysql.connect(host="127.0.0.1",user="lepus",password="3c905b43cyy",port=3306,charset="utf8",database='lepus')
sql1="select id,host,port,tags,send_slowquery_to_list from db_servers_mysql where slow_query=1 and send_slowquery_to_list != '' ;"
#sql1="select id,host,port,tags,send_slowquery_to_list from db_servers_mysql where slow_query=1 and send_slowquery_to_list != '' and id=13;"
cursor=conn.cursor(cursor=pymysql.cursors.DictCursor)


cursor.execute(sql1)
data1=cursor.fetchall()
for i in data1:
    id=i["id"]
    host=i['host']
    port=i['port']
    tags=i['tags']
    send_slowquery_to_list=i['send_slowquery_to_list'].split(";")
    #sql2 = "select review.*,history.* from mysql_slow_query_review review join mysql_slow_query_review_history history on review.`checksum`=history.checksum and db_max='tbj' and serverid_max='%s' and db_max!='information_schema' and fingerprint!='commit' and user_max!='root' and ts_min>'%s' and ts_max<'%s' and ts_cnt>500  order by  ts_cnt desc ;"
    sql2 = "select review.*,history.* from mysql_slow_query_review review join mysql_slow_query_review_history history on review.`checksum`=history.checksum and serverid_max=%s and db_max!='information_schema' and fingerprint!='commit' and user_max!='root' and ts_min>'%s' and ts_max<'%s' and ts_cnt>500  order by  ts_cnt desc ;"

#    print(sql2)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql2 % (id,first_seen_set,last_seen_set))
    data2 = cursor.fetchall()
    content=''
    if len(data2)>0:
        cnt=1
        for e_data2 in data2:
            checksum=e_data2["checksum"]
            db_max=e_data2['db_max']
            user_max=e_data2['user_max']
            fingerprint=e_data2['fingerprint']
            sample_tmp = e_data2['sample']
            ts_cnt = e_data2['ts_cnt']
            Query_time_sum = e_data2['Query_time_sum']
            Query_time_max = e_data2['Query_time_max']
            Lock_time_max = e_data2['Lock_time_max']
            Rows_sent_max = e_data2['Rows_sent_max']
            Rows_examined_max = e_data2['Rows_examined_max']
            ts_min = e_data2['ts_min']
            ts_max = e_data2['ts_max']
            sample=''
            for e_s in sample_tmp.splitlines():
                if len(e_s) != 0 and not e_s.isspace():
                    sample=sample.__add__(e_s).__add__("\t")
                    sample_out=re.sub(r"\s{2,}"," ",sample)+';'
                    #sample_out=replaceAll('  ', ' ',  sample)
            content_tmp="------" + "\n"+ "慢SQL:" + str(cnt) +"\n" +"库名:" + db_max + "\n"+ "用户:"+user_max  +"\n"+"首次出现:" + str(ts_min) + "\n"+ "末次出现:" + str(ts_max) + '\n' + "次数："+str(ts_cnt)+'\n'+ "慢SQL详情：" + sample_out +"\n"+ "最大执行时间:" + str(Query_time_max) + "\n" + "最多发送行数:" + str(Rows_sent_max) +"\n" + "最多扫描行数:" + str(Rows_examined_max) + "\n" + "------" + "\n"
            content = content.__add__(content_tmp)
            cnt=cnt+1
        #print(sample_out)
        #print(content)
        strTitle="您的数据库实例:["+tags+"]发现慢查询请及时优化"
        strContent="HI ALL:\n下面的慢查询语句或许会影响到数据库的稳定性和健康性，请您在收到此邮件后及时优化语句或代码。数据库的稳定性需要大家的共同努力，感谢您的配合！\n(慢查询统计规则：统计前一日，执行大于1s，总次数超过500次的查询SQL。)\n"+"标签：" +tags +"\n" + str(content) + "\n\n--\n\n慢查询自动推送邮件"
        m=MailSender()
        m.sendEmail(strTitle,strContent,send_slowquery_to_list)
    else:
        strContent="标签：" +tags +"\n"+"恭喜：昨天没有慢查询产生！！\n(慢查询统计规则：统计前一日，执行大于1s，总次数超过500次的查询SQL。)\n\n\n--\n\n慢查询自动推送邮件"
        strTitle="您的数据库实例:["+tags+"]未发现慢查询"
        m = MailSender()
        send_slowquery_to_list_other=['tianyuan@tongbanjie.com']
        m.sendEmail(strTitle, strContent, send_slowquery_to_list_other)

conn.close()
