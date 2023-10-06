## 安装awscli
```bash
## x86_64
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" 
unzip awscliv2.zip 
sudo ./aws/install

## arm
curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip" 
unzip awscliv2.zip 
sudo ./aws/install

配置 aws configure

```

## 安装python环境

```bash
apt-get install python3.9
```



## 安装依赖

```bash
pip install -r requirements.txt
```

## 修改密码
```bash
sed -i 's/yourcode/yourpass/g' app.py
```

## 运行

```bash
nohup python3 app.py &
```

