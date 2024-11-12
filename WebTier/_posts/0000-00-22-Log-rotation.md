---
date: 2024-10-30 14:41:56 +0900
layout: post
title: "[WebTier/OHS/Apache] Log rotation"
tags: [WebTier, OHS, Apache, Log, Rotation]
typora-root-url: ..
---

# 1. Overview
Apache 2.X를 Based로 하는 Oracle HTTP Server 에서의 Log rotation 설정 방법


<br><br>

<br>

# 2. Descriptions
ErrorLog 지시어를 예시로 다음과 같이 지정 할 수 있다.

`ErrorLog "||${PRODUCT_HOME}/bin/odl_rotatelogs ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/error-%Y-%m-%d 10M 100M"`

- 모든 로그는 error 파일에 기록된다.
- error 파일이 용량 10Mbytes에 도달하면, error-%Y-%m-%d-%H 으로 회전한다.
- error 파일 및 회전된 파일들이 10개(100Mbytes)로 유지되며, 초과 시 가장 오래된 로그가 삭제된다.
- 로그가 회전되는 주기보다 더 빠르게 쌓이면 timestamp format을 더 낮은 레벨까지 확장해야 유실되는 로그가 없다.

<br>

`ErrorLog "||${PRODUCT_HOME}/bin/odl_rotatelogs -u:32400 ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/error-%Y-%m-%d 86400 172800"`

- -u(offset) 을 32400 seconds로 하여, KST 기준 자정(00시)마다 회전한다

- frequency(86400 seconds)마다 회전 한다.

- retentionTime(172800 seconds)동안 회전된 파일들을 보관한다. (아래 실제 보관된 예시)

- ```sh
  -rw-r----- 1 root     weblogic  362854 Oct 15 23:59 error-2024-10-16
  -rw-r----- 1 root     weblogic  723262 Oct 16 23:59 error-2024-10-17
  -rw-r----- 1 root     weblogic 1512949 Oct 17 23:59 error-2024-10-18
  -rw-r----- 1 root     weblogic   44393 Oct 18 00:00 error
  ```


<br><br>


# 3. References

[9 Managing Oracle HTTP Server Logs](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/man_logs.html)

**Oracle HTTP Server에서 Log file을 Rotation 하는 방법 (Doc ID 3053592.1)**