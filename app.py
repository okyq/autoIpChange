from flask import Flask, render_template, request, jsonify
import boto3
import requests

app = Flask(__name__)
logs = []


def print_log(log):
    print(log)
    logs.append(log)

# 业务逻辑代码
def execute_business_logic(instance_name, record_names, api_key, email, zone_id, region_name):
    # 将print的日志保存到一个列表中

    # 将参数传递给业务逻辑代码
    instance_name = instance_name.strip()
    record_names = [name.strip() for name in record_names.split(',')]
    api_key = api_key.strip()
    email = email.strip()
    zone_id = zone_id.strip()
    region_name = region_name.strip()
    if len(region_name) > 2:
        # 创建Lightsail客户端
        client = boto3.client('lightsail', region_name=region_name)
    else:
        client = boto3.client('lightsail')
    # 获取实例信息
    instance_response = client.get_instance(instanceName=instance_name)
    instance = instance_response['instance']

    # 获取实例的 IP 地址
    ip_address = instance['publicIpAddress']
    print_log(f'获取到实例IP：{ip_address}')

    # 获取 IP 地址的名称
    ip_response = client.get_static_ips()
    static_ips = ip_response['staticIps']
    ip_name = None

    for ip in static_ips:
        if ip['ipAddress'] == ip_address:
            ip_name = ip['name']
            print_log(f'获取到实例IP名称：{ip_name}')
            break

    if ip_name is None:
        print_log('无法找到与实例关联的 IP 地址名称')
        exit()

    # 分离实例的 IP 地址
    client.release_static_ip(staticIpName=ip_name)
    print_log(f'实例{instance_name}和Ip{ip_address}分离成功')

    # 生成新的 IP 地址
    new_ip = client.allocate_static_ip(staticIpName=ip_name)
    print_log(f'新ip生成成功,ipName:{ip_name}')

    # 将新的 IP 地址附加到实例上
    client.attach_static_ip(staticIpName=ip_name, instanceName=instance_name)
    print_log(f'已经将新的ip{ip_name}附加到实例{instance_name}上')

    client.close()
    print_log('关闭lightsailClient')

    if len(region_name) > 2:
        # 创建Lightsail客户端
        client = boto3.client('lightsail', region_name=region_name)
    else:
        client = boto3.client('lightsail')
    print_log('创建新的lightsailClient')
    # 获取实例信息
    instance_response = client.get_instance(instanceName=instance_name)
    instance = instance_response['instance']

    # 获取实例的 IP 地址
    new_ip_address = instance['publicIpAddress']
    print_log(f'获取到实例IP：{new_ip_address}')
    print_log('开始修改cloudflareDNS解析。。。。。')

    # 获取指定名称和标签的DNS记录ID
    def get_dns_record_id(name):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={name}'
        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_key,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                return data['result'][0]['id']
        return None

    # 修改DNS记录
    def change_dns_record(record_names, record_type, content):
        for name in record_names:
            record_id = get_dns_record_id(name)
            if record_id:
                update_dns_record(record_id, name, record_type, content)
            else:
                print_log(f'找不到名称为 {name} 的DNS记录，无法修改')

    # 修改DNS记录
    def update_dns_record(record_id, name, record_type, content):
        url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
        headers = {
            'X-Auth-Email': email,
            'X-Auth-Key': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'type': record_type,
            'name': name,
            'content': content
        }
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200:
            print_log(f'DNS记录 {name} 指向：{content}修改成功')
        else:
            print_log(f'修改DNS记录 {name} 指向：{content}失败')

    change_dns_record(record_names, 'A', new_ip_address)

    # 执行业务逻辑代码
    # ...

    return logs


# ----------------------------------------------------- dns相关----------------------------------------------：
def get_dns_record_id(name, zone_id, email, api_key):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?type=A&name={name}'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['result']:
            return data['result'][0]['id']
    return None


# 创建DNS记录
def create_dns_record(name, record_type, content, zone_id, email, api_key):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'type': record_type,
        'name': name,
        'content': content
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return f'DNS记录 {name} 创建成功'
    else:
        return f'创建DNS记录 {name} 失败'


# 修改DNS记录
def update_dns_record(record_id, name, record_type, content, zone_id, email, api_key):
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}'
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
    }
    data = {
        'type': record_type,
        'name': name,
        'content': content
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 200:
        return f'DNS记录 {name} 修改成功'
    else:
        return f'修改DNS记录 {name} 失败'


# 新增或修改DNS记录
def change_dns_record(record_names, record_type, content, tag, zone_id, email, api_key):
    record_names = [name.strip() for name in record_names.split(',')]
    for name in record_names:
        record_id = get_dns_record_id(name, zone_id, email, api_key)
        if tag == '1':
            if record_id:
                print_log(f'名称为 {name} 的DNS记录已存在，无法新增')
            else:
                print_log(create_dns_record(name, record_type, content, zone_id, email, api_key))
        elif tag == '2':
            if record_id:
                print_log(update_dns_record(record_id, name, record_type, content, zone_id, email, api_key))
            else:
                print_log(f'找不到名称为 {name} 的DNS记录，无法修改')
        else:
            print_log('无效的标签')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/execute', methods=['POST'])
def execute():
    logs.clear()
    password = request.form.get('password')
    if password != 'xxx': #输入一个校验码
        return jsonify({'error': 'Invalid password'})

    instance_name = request.form.get('instance_name')
    record_names = request.form.get('record_names')
    api_key = request.form.get('api_key')
    email = request.form.get('email')
    zone_id = request.form.get('zone_id')
    region_name = request.form.get('region_name')

    record_type = request.form.get('record_type')
    record_content = request.form.get('record_content')
    tag = request.form.get('tag')
    isDnsOnly = request.form.get('isDnsOnly')
    print(request.form)
    print(tag)
    if isDnsOnly is not None and isDnsOnly == "on":
        change_dns_record(record_names, record_type, record_content, tag, zone_id, email, api_key)
    else:
        execute_business_logic(instance_name, record_names, api_key, email, zone_id, region_name)

    return jsonify({'logs': logs})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8179)
