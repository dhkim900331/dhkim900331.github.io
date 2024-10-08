---
date: 2024-10-08 16:44:22 +0900
layout: post
title: "[JDBC] How to use keepalive?"
tags: [JDBC, keepalive]
typora-root-url: ..
---

# 1. Overview
JDBC Connection에 Keepalive 사용 방법


# 2. Descriptions
Oracle JDBC Thin Driver에서 Keepalive 기능은
Connect url description 에 ENABLE=BROKEN 으로 활성화 한다.

또한, JDBC Driver에 keepalive 활성화 외에 다른 설정 가능한 매개변수는 직접적으로 없고
OS level에 매개변수인 tcp_keepalive_time, tcp_keepalive_interval, tcp_keepalive_probes 를 사용한다.

 - tcp_keepalive_time : 해당 Seconds 동안 TCP 연결이 비활성 상태일 때, keepalive 패킷을 보낸다.
 - tcp_keepalive_interval : 첫 keepalive 패킷에 응답이 없으면, 해당 Seconds 간격마다 keepalive 패킷을 보낸다.
 - tcp_keepalive_probes : keepalive 패킷을 주기적으로 보낼 때, 최대 몇 회 반복할지를 정한다.

즉, 다음과 같이 활성화 하면 OS TCP/IP 수준에서 Keepalive packet을 주고받는다.
jdbc:oracle:thin:@(DESCRIPTION=(ENABLE=BROKEN)(ADDRESS=(PROTOCOL=tcp)(PORT=<PORT>)(HOST=<HOST>))(CONNECT_DATA=(SERVICE_NAME=<SERVICE_NAME>)))


# 3. References
[JDBC Developer's Guide : Troubleshooting](https://docs.oracle.com/en/database/oracle/oracle-database/19/jjdbc/JDBC-troubleshooting.html#GUID-D4FEB9D7-D7F2-4AF8-858C-89E3988CD00D)
Oracle Net 12c: Changes to the Functionality of Dead Connection Detection (DCD) (Doc ID 1591874.1)	