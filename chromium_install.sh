#!/bin/bash

# 安装函数
install_dependencies() {
  echo "开始安装依赖..."
    sudo apt update -y && sudo apt upgrade -y
    for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

    sudo apt-get update
    sudo apt-get install ca-certificates curl gnupg
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update -y && sudo apt upgrade -y

    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Docker version check
    docker --version

  echo "依赖安装完成。"
}

# 配置函数
configure_service() {
  echo "开始配置服务..."
    
  # 提示用户输入用户名和密码
  read -p "请输入用户名: " username
  read -sp "请输入密码: " password
  echo
  realpath --relative-to /usr/share/zoneinfo /etc/localtime
  mkdir -p ~/chromium
  cd ~/chromium

  # 定义docker-compose.yaml文件路径
  compose_file="docker-compose.yaml"

  # 如果文件不存在，创建一个新的文件并写入默认内容
  if [ ! -f "$compose_file" ]; then
    echo "文件 $compose_file 不存在，正在创建..."
    cat <<EOL > $compose_file
services:
  chromium:
    image: lscr.io/linuxserver/chromium:latest
    container_name: chromium
    security_opt:
      - seccomp:unconfined #optional
    environment:
      - CUSTOM_USER=$username
      - PASSWORD=$password
      - PUID=1000
      - PGID=1000
      - TZ=Europe/London
      - CHROME_CLI=https://x.com/0xbillzkp
    volumes:
      - /root/chromium/config:/config
    ports:
      - 3010:3000   #Change 3010 to your favorite port if needed
      - 3011:3001   #Change 3011 to your favorite port if needed
    shm_size: "1gb"
    restart: unless-stopped
EOL
  else
    # 使用sed命令替换docker-compose.yaml文件中的占位符
    sed -i.bak "s/CUSTOM_USER=.*/CUSTOM_USER=$username/" "$compose_file"
    sed -i.bak "s/PASSWORD=.*/PASSWORD=$password/" "$compose_file"
  fi

  echo "服务配置完成。"
}

# 启动服务函数
start_service() {
  echo "开始启动服务..."
  cd $HOME && cd chromium
  docker compose up -d
  echo "服务已启动。"
}

stop_service() {
  echo "开始停止服务..."
  cd $HOME && cd chromium
  docker stop chromium
  echo "服务已停止。"
}

# 测试服务函数
test_service() {
  echo "测试服务是否已启动..."
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3010)
  if [ "$response" -eq 200 ]; then
    echo "服务已成功启动并运行。"
  else
    echo "服务未能成功启动。HTTP 状态码: $response"
  fi
}
# 主菜单
main_menu() {
  echo "请选择操作："
  echo "1) 安装依赖"
  echo "2) 配置服务"
  echo "3) 启动服务"
  echo "4) 停止服务"
  echo "5) 测试服务"
  echo "6) 退出"
  read -p "请输入选项 (1-5): " choice

  case $choice in
    1)
      install_dependencies
      ;;
    2)
      configure_service
      ;;
    3)
      start_service
      ;;
    4)
      stop_service
      ;;  
    5)
      test_service
      ;;      
    6)
      exit 0
      ;;
    *)
      echo "无效选项，请重新选择。"
      main_menu
      ;;
  esac
}

# 运行主菜单
main_menu
