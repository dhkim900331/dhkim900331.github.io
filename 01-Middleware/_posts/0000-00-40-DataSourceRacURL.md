---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[Middleware/WebLogic] 데이터소스 RAC URL"
tags: [Middleware, WebLogic, DataSource, RAC, URL]
typora-root-url: ..
---

# 1. 개요

데이터소스 RAC URL




# 2. 설명

(1). `$ORACLE_HOME/network/admin/tnsnames.ora`에서 `host, port, service_name`을 캐치 하여 아래 URL 적용

```
jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbhost1)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=dbhost2)(PORT=1521)))(FAILOVER=on)(LOAD_BALANCE=off)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=dbservice.company_name.com))))
```

> 괄호 갯수에 주의하자. URL이 잘못되면 NL Exception, SO Exception이 떨어진다. (다른 이유로 떨어질 수도 있다.)



# 3. 기타

(1). MDS 권장

RAC환경 구성시 WLS 12c에서 Deprecated된 CTF 방식의 failover보다는

Multi DataSource 방식의 failover을 사용하시기 바랍니다.

[D Using Connect-Time Failover with Oracle RAC (Deprecated)](https://docs.oracle.com/cd/E24329_01/web.1211/e24367/connecttime.htm)



Oracle RAC 사용시 Multi datasource를 사용하는 것은 datasource pool을 미리 만들어 놓기 때문에 fail-over가 빠르다는 장점이 있습니다.

weblogic server가 부팅될때 미리 RAC1과 RAC2를 각각 만들어 놓고 RAC1에서 Test fail이 감지되면 RAC2로 getConenction을 시도하게 됩니다.



(2). RAC 사용시 CTF 방식의 failover 이슈 관련하여 JDBC 쪽 문서가 확인됩니다.

관련문서: JDBC Connections Hang On Socketread0 After RAC Failover ( Doc ID 1386017.1 )
