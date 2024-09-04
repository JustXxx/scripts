#!/bin/bash

# 安装Dante
sudo apt-get update
sudo apt-get install -y dante-server

# 获取第一个非本地网络接口的名称
INTERFACE=$(ip -o -4 route show to default | awk '{print $5}')

# 创建Dante配置文件
cat << EOF > /etc/danted.conf
logoutput: /var/log/danted.log
internal: $INTERFACE port = 22233
external: $INTERFACE
socksmethod: username
user.privileged: root
user.unprivileged: nobody

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    log: error
}
EOF

# 创建Dante用户
sudo useradd --shell /usr/sbin/nologin danteuser
echo "danteuser:ww86x22r6df" | chpasswd

# 启动Dante服务
sudo systemctl start danted
sudo systemctl enable danted
sudo systemctl status danted
