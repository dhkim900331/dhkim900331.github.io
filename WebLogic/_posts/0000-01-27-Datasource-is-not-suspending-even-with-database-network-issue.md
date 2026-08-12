---
date: 2026-07-03 18:06:17 +0900
layout: post
title: "[WebLogic/Datasource] Datasource is not suspending even with database network issue"
tags: [Middleware, WebLogic, Datasource]
typora-root-url: ../..
---

# 1. Overview

2개의 동일 구성 A/B Datasource 환경에서,

DB와의 Network 장애로 인해 Connection이 정리되지 않은 사례.

<br><br>


# 2. Descriptions

A/B Datasource 는 다음과 같은 설정값이 적용되어 있다.

```xml
   <initial-capacity>10</initial-capacity>
   <max-capacity>100</max-capacity>
   <min-capacity>10</min-capacity>
   <test-frequency-seconds>120</test-frequency-seconds>
   <test-connections-on-reserve>true</test-connections-on-reserve>
```

<br>

A Datasource는 Connection testing 과정을 통해 suspending 진입을 하여, Connection 정리 과정이 진행되었고,

```
<Info> <Common> <BEA-000633> <Resource Pool "A" suspending due to consecutive number of resource creation failures exceeding threshold of 2>
```

<br>

B Datasource는 위와 같은 일련의 과정이 전무하여, 오랜 시간 Hang 상태에 머물러 있었다.

B Datasource가 실행되는 Weblogic Server 측에 Thread 들은, 이미 Connection을 받아 SQL Query 실행 중에 있었고

DB Network issue로 인해 무기한 hang 에 빠져 있었다.

```
<Error> <WebLogicServer> <BEA-000337> <[STUCK] ExecuteThread: '5' for queue:
", which is more than the configured time (StuckThreadMaxTime) of "600" seconds in "server-failure-trigger". Stack trace:
    sun.nio.ch.FileDispatcherImpl.read0(Native Method)
    ...
    org.apache.ibatis.executor.statement.PreparedStatementHandler.query(PreparedStatementHandler.jav a:65)
```

<br>

A Datasource는 모든 Connection이 점유(In-use)되어 있지 않았고,

IDLE Connection 대상으로 120초 간격 또는 getConnection에 의해 할당되기 직전에 Connection을 점검하여

DB 쪽과 물리적으로 네트워크 연결에 문제가 있음을 감지하여 Suspending 상태에 진입할 수 있었다.

<br>

반면 B Datasource는 Maximum capacity 100개 Connection 모두가 이미 App에 할당되어

IDLE Connection이 전무한 상태였다.

게다가 query read timeout 과 같은 속성값이 정의되어 있지 않아 무기한 대기 상태이다.

<br>

Datasource는 문제 없이 구성되어 있으므로, DB와의 통신에 문제가 있다면 A Datasource 처럼 정리가 되지만,

App 레벨에서 쥐고 있는 사실상 Dead Connection은 Datasource에서 관리하지 않으므로 이러한 문제가 발생한다.

<br>

App에서 이미 사용 중인 In-use connection의 timeout 값을

Datasource - Configuration - Connection Pool - Properties 에 정의하고

```
oracle.jdbc.ReadTimeout = <msecs>
```

<br>

Advanced - Statement Timeout (secs) 을 정의한다.

<br>

ReadTimeout은 JDBC Driver Level에서 Socket 을 끊을 수 있지만,

Statement Timeout은 slow query를 끊기 위해 "cancel" 요청을 DB측에 전달하기 때문에 네트워크 장애시에는 의미있는 동작을 기대하기 어렵다.


<br><br>


# 3. References

How to Protect Connection Pool from Being Exhausted - KB626459

데이터소스가 네트워크 장애를 감지하지 못하여 중단되지 않습니다. - KB885116
