---
date: 2026-07-15 20:04:15 +0900
layout: post
title: "[WebTier/OHS] OPMN Ping hung because of WebLogic Proxy Plugin"
tags: [WebTier, OHS, ]
typora-root-url: ../..
---

# 1. Overview

OHS Instance가 OPMN Ping에 응답하지 못하고 Shutdown 됩니다.

<br><br>


# 2. Descriptions

OHS 11gR1 OPMN은 주기적으로 OHS Instance 의 Health Check를 위해 Ping을 전송하고 결과를 수신합니다.

[OPMN Element/Attribute 참고](https://docs.oracle.com/cd/E28280_01/doc.1111/e14007/common.htm#BABJIHHI)

[OPMN Automatic Restart 참고](https://docs.oracle.com/cd/E28280_01/doc.1111/e14007/opmnxml.htm#i1023495)

<br>

`opmnctl` 도구로 OHS Instance 기동 후 얼마 지나지 않아 time out으로 인해 기동 되었던 OHS Instance가 죽게 됩니다.

```
./opmnctl startall
opmnctl startall: starting opmn and all managed processes...
================================================================================
opmn id=localhost.localdomain:6701
Response: 0 of 1 processes started.

ias-instance id=instance1
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
--------------------------------------------------------------------------------
ias-component/process-type/process-set:
 component1/OHS/OHS/

Error
--> Process (index=1,uid=2056550977,pid=6412)
 time out while waiting for a managed process to start
 Log:
 /home/ohs/ohs11119/oracle_wt1/instances/instance1/diagnostics/logs/OHS/component1/console~OHS~1.log
```

<br>

OPMN 의 HEAD /index.html 요청이 잠깐 동안 기동된 OHS Instance로 주기적으로 전달됩니다.

```
127.0.0.1 - - [02/Jul/2026:14:06:29 +0900] "HEAD  /index.html HTTP/1.1" 503 -
127.0.0.1 - - [02/Jul/2026:14:07:01 +0900] "HEAD  /index.html HTTP/1.1" 503 -
127.0.0.1 - - [02/Jul/2026:14:07:33 +0900] "HEAD  /index.html HTTP/1.1" 503 -
127.0.0.1 - - [02/Jul/2026:14:08:05 +0900] "HEAD  /index.html HTTP/1.1" 503 -
127.0.0.1 - - [02/Jul/2026:14:08:37 +0900] "HEAD  /index.html HTTP/1.1" 503 -
```

<br>

OHS Instance에는 WebLogic Proxy Plugin 설정 중 확장자 옵션이 모든 것을 수신하도록 되어 있습니다.

```
MatchExpression *
```

<br>

OPMN Head 요청이 WebLogic 으로 전달되지만, WebLogic Instance가 Shutdown 되어 있어 요청을 처리 하지 못합니다.

또한 Proxy Plugin의 실패 요청 재시도 로직으로 인해 더 오랫동안 반복 합니다.

```
2026-07-02T17:21:22.0212+09:00 ... ================New Request: [HEAD  /index.html HTTP/1.1] =================
2026-07-02T17:21:22.0213+09:00 ... attempt #0 out of a max of 5
2026-07-02T17:21:22.0215+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:22.0215+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:24.0286+09:00 ... attempt #1 out of a max of 5
2026-07-02T17:21:24.0289+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:24.0289+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:26.0346+09:00 ... attempt #2 out of a max of 5
2026-07-02T17:21:26.0348+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:26.0349+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:28.0450+09:00 ... attempt #3 out of a max of 5
2026-07-02T17:21:28.0452+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:28.0453+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:30.0482+09:00 ... attempt #4 out of a max of 5
2026-07-02T17:21:30.0485+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:30.0486+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:32.0578+09:00 ... attempt #5 out of a max of 5
2026-07-02T17:21:32.0580+09:00 ... *******Exception type [CONNECTION_REFUSED] (apr_socket_connect call failed with error=111, host=<HOST>, port=<PORT> ) raised at line 1611 of URL.cpp
2026-07-02T17:21:32.0581+09:00 ... Sleeping for 2 seconds


2026-07-02T17:21:34.0605+09:00 ... request [/index.html] did NOT process successfully..................
```

<br>

Health Check 요청이 WLS에 도달하지 않게 하기 위해, `MatchExpression *.jsp` 등으로 구성을 변경하여 문제가 해결 되었습니다.

<br><br>


# 3. References

How to stop logging OPMN Ping in access.log (KB351995)

OPMN Ping이 처리 되지 않아 OHS Instance가 중지됩니다. (KB918735)
