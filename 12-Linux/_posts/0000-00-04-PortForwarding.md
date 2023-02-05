---
date: 2022-10-06 17:15:38 +0900
layout: post
title: "[linux/putty] Port Forwarding"
tags: [os, linux, putty, port, forwarding]
typora-root-url: ..
---

# 1. 개요

접속 하려는 Port가 방화벽 등의 문제로 접속을 할 수 없다면,

putty.exe 또는 ssh command의 Port Forwarding 기능으로 해결할 수 있다.



# 2. putty.exe

Target Server 에 TCP Port Listen 되어 있으나, 방화벽 등으로 직접 TCP Port 에 Access 할 수 없을 때,

putty 의 Port Forwarding 기능을 사용하여 접속할 수 있다.



TCP 8081 Listen 상태 확인

```sh
$ netstat -an | grep 8081 | grep LISTEN
tcp        0      0 192.168.56.2:8081       0.0.0.0:*               LISTEN
```



방화벽으로 인해

```sh
$ sudo systemctl status firewalld
● firewalld.service - firewalld - dynamic firewall daemon
   Loaded: loaded (/usr/lib/systemd/system/firewalld.service; disabled; vendor preset: enabled)
   Active: active (running) since Thu 2022-10-06 15:47:49 KST; 1s ago
     Docs: man:firewalld(1)
 Main PID: 1515 (firewalld)
   CGroup: /system.slice/firewalld.service
           └─1515 /usr/bin/python2 -Es /usr/sbin/firewalld --nofork --nopid

```



서버외부에서 TCP 8081 호출할 수 없다.

![PortForwarding_1](/../assets/posts/images/12-Linux/PortForwarding/PortForwarding_1.png)



putty.exe의 SSH - Tunnels 에서 Target Address 를 설정한다.

(사진에서 Add 버튼 까지 눌러야 설정이 완료.)

![PortForwarding_2](/../assets/posts/images/12-Linux/PortForwarding/PortForwarding_2.png)



Windows CMD로 localhost:8081 이 LISTENING 되어 있는 것이 확인 된다.

이는, putty.exe가 LISTEN을 하고 있는 것이다.

![PortForwarding_3](/../assets/posts/images/12-Linux/PortForwarding/PortForwarding_3.png)



localhost:8081 접속 시, putty.exe가 proxy 역할을 수행한다.

![PortForwarding_4](/../assets/posts/images/12-Linux/PortForwarding/PortForwarding_4.png)



# 3. ssh

putty.exe를 사용할 수 있는 구간은, Client가 Target Server 바로 앞일 때이다.

Bastion 환경 등과 같이 단순한 구조가 아닐 때는, ssh command 를 사용해야 한다.



상황은 다음과 같다고 가정한다.

* Client - Bastion - Target

* 현재 모든 구간은 SSH Port 접근만 가능하다.
* Target에 8001 TCP Port로 Service 가 Listen 되고 있다.
* Client도, Bastion도 Target의 8001 TCP Port를 호출할 수 없도록, 방화벽이 설정되어 있다.



Bastion 에서 다음과 같이 ssh command 를 입력한다.

```sh
$ ssh -L <Bastion IP>:8001:<Target IP>:8001 <Target USER>@<Target IP> -p <Target SSH Port>
```



* 시작 부분을 반드시 <Bastion IP\> 로 지정한다. (Bastion을 Proxy 로 이용하기 때문에, localhost 로 지정하면 안된다.)

* Bastion 내에  TCP 8001 이 Listen 된다.
* Bastion 내에 <Bastion IP\>:8001 Traffic 은 <Target IP\>:8001 으로 Forward 된다.
* 이 과정을 위해, <Target USER\>@<Target IP\> -p <Target SSH Port\> 정보로 ssh 인증을 수행한다.



여기까지 수행이 되면, Bastion 에서 다음 명령어 수행 시, TCP 8001 Port 에 Access 할 수 있다.

```sh
$ curl <Bastion IP>:8001
```



putty.exe 의 Tunnels 기능을 통해, Client - Bastion 구간을 다음과 같이 설정하면, Client의 Browser 를 통해 Target Port에 Access 할 수 있다.

![PortForwarding_5](/../assets/posts/images/12-Linux/PortForwarding/PortForwarding_5.png)



* putty.exe는 TCP 8001 으로 들어오는 Traffic을 Bastion 의 TCP 8001 으로 Forward 한다.
* Bastion 은 (위에서 설명한 것과 같이) Target 의 TCP 8001 으로 Forward 한다.
