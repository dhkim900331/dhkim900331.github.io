---
layout: post
title: "[Linux] How to use iptables (BASIC)"
tags: [Linux, OS, iptables, firewalld]
typora-root-url: ..
---

# 1. Overview
Linux의 iptables 의 간단한 사용법


# 2. Descriptions
```sh
$ sudo systemctl start iptables
$ sudo iptables -F
$ sudo iptables -P INPUT ACCEPT
$ sudo iptables -P FORWARD ACCEPT
$ sudo iptables -P OUTPUT ACCEPT
$ sudo iptables -A INPUT -p tcp --dport 8001:8003 -j REJECT
$ sudo iptables -L -n -v
Chain INPUT (policy ACCEPT 9 packets, 657 bytes)
 pkts bytes target     prot opt in     out     source               destination
    0     0 REJECT     tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp dpts:8001:8003 reject-with icmp-port-unreachable

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 5 packets, 584 bytes)
 pkts bytes target     prot opt in     out     source               destination
```

 - iptables 서비스 시작과, `-F` 옵션으로 모든 설정을 초기화 한다.
 - iptables 는 기본적으로 모든 트래픽을 REJECT 하므로 INPUT/FORWARD/OUTPUT 정책을 ACCEPT로 전환하여 모든 트래픽을 허용 한다.
 - 8001 ~ 8003 TCP 트래픽을 REJECT 하도록 한다.
 - 지정한 규칙을 `-L -n -v` 으로 출력한다.



```sh
$ sudo iptables -L INPUT -n --line-numbers
Chain INPUT (policy ACCEPT)
num  target     prot opt source               destination
1    REJECT     tcp  --  0.0.0.0/0            0.0.0.0/0            tcp dpts:8001:8003 reject-with icmp-port-unreachable

$ sudo iptables -D INPUT 1
```

 - 저장된 규칙의 번호로 삭제할 수 있다.