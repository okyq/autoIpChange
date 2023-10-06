import smtplib
import requests
from email.mime.text import MIMEText
from email.header import Header

# 将脚本导入华为函数工作流，设置频率，实现自动更换被墙节点IP

url = ''  # 接口
password = ''  # 校验码
log_result = []
data_1 = {
    'password': password,
    'instance_name': '',
    'record_names': '',
    'api_key': '',
    'email': '',
    'zone_id': '',
    'region_name': '',
    'record_type': 'A',
    'tag': '2',
    'isDnsOnly': ''
}
data_2 = {
    'password': password,
    'instance_name': '',
    'record_names': '',
    'api_key': '',
    'email': '',
    'zone_id': '',
    'region_name': '',
    'record_type': '',
    'tag': '2',
    'isDnsOnly': ''
}
check_domain_1 = 'https://xxx.xxx'
check_domain_2 = 'https://xx.xxx.xx'


def send_email(subject, body):
    sender_email = ""
    sender_password = ""
    receiver_email = ""

    message = f"Subject: {subject}\n\n{body}"
    # 创建邮件对象
    msg = MIMEText(body, 'plain', 'utf-8')
    # 设置邮件头部信息
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())


def check_server_status(domain):
    try:
        response = requests.get(domain, timeout=50)
        print(response)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error occurred while checking server status: {e}")
        return False


def change_ip(data):
    # 发送POST请求
    response = requests.post(url, data=data, verify=False)
    result = response.json()
    logs = result['logs']
    for log in logs:
        print(log)
        log_result.append(log)
    # 处理响应
    if response.status_code == 200:
        return True
    else:
        return False


def check_change_send(check_domain, data):
    log_result.clear()
    server_status = check_server_status(check_domain)
    if server_status:
        subject = f"{check_domain} Status: OK"
        body = f"The server at {check_domain} is online and reachable."
    else:
        if change_ip(data):
            subject = f"Change Ip Success,{check_domain} Status: NOTOK"
            body = f"SUCCESS!!->The server at {check_domain} is offline or unreachable.IP update successful.Try xray again later\n Logs:\n{log_result}"
        else:
            subject = f"Change Ip Failed,{check_domain} Status: NOT OK"
            body = f"FAILED!!->The server at {check_domain} is offline or unreachable.IP update failed.Try again 10min later\n Logs:\n{log_result}"
        # 只在错误情况下发送邮件
        send_email(subject, body)


def handler(event, context):
    check_change_send(check_domain_1, data_1)
    check_change_send(check_domain_2, data_2)
