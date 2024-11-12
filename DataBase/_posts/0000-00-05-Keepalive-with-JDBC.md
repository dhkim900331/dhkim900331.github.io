---
date: 2024-10-08 16:44:22 +0900
layout: post
title: "[Database/JDBC] Keepalive with JDBC"
tags: [Database, JDBC, Keepalive, DCD, Firewall]
typora-root-url: ..
---

# 1. Overview
JDBC Thin Driver에서 Keepalive 구성 방법


<br><br>

<br>

# 2. Descriptions
## 2.1 Client side
JDBC URL Description 절에 ENABLE=BROKEN 을 적용하면, Keepalive이 활성화 된다.
Keepalive time 옵션값은 JDBC에 매개변수가 존재하지 않아, Linux OS의 `tcp_keepalive_time, tcp_keepalive_interval, tcp_keepalive_probes` 파라메터들에 의존한다.

 - tcp_keepalive_time : 기본값 7200초. 해당 시간 동안 Connection 을 유지한다.
 - tcp_keepalive_interval : Keepalive packet을 보내고 응답이 없으면, 해당 시간 이후 재시도 한다.
 - tcp_keepalive_probes : tcp_keepalive_interval 의 반복횟수


<br><br>


## 2.2 Server side
`2.1 Client Side` 는 JDBC Driver 수준에서 설정하고, TCP/IP 수준에서 주고받는 Packet으로 Keepalive 가 유지된다.
DB Server side에서는 sqlnet.ora 에 SQLNET.EXPIRE_TIME=1 속성값을 설정해, 1분마다 연결되어 있는 JDBC Connection의 health를 확인한다.

Oracle NET DCD(Dead Connection Detection) 이라고 하며, TCP/IP 수준이 아닌 Oracle NET 세션 수준에서 이뤄지며,
일반적으로 Client Side만으로도 충분하겠지만 양측에서 교차 검증하도록 하여 신뢰성을 높일 수 있다.


<br><br>


# 3. References
[E.1.5 Using JDBC with Firewalls and E.1.6 Frequent Abrupt Disconnection from Server](https://docs.oracle.com/en/database/oracle/oracle-database/19/jjdbc/JDBC-troubleshooting.html#GUID-5ADA932F-B2BF-4E34-8995-435FD2EF1F92)
