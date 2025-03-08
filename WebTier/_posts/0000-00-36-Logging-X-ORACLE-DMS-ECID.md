---
date: 2025-03-08 10:18:06 +0900
layout: post
title: "[WebTier/OHS] Logging for X-ORACLE-DMS-ECID"
tags: [WebTier, OHS, DMS]
typora-root-url: ..
---

# 1. Overview

X-ORACLE-DMS-ECID Header를 Apache Logging 하는 방법


<br><br>


# 2. Descriptions

해당 Header는 DMS 기능이 기본적으로 활성화 되어 있어, Oracle Fusion Middleware 에서 생성 됩니다.

DMS 에 대한 내용은 [About Dynamic Monitoring Service (DMS)](https://docs.oracle.com/en/middleware/fusion-middleware/14.1.2/asper/using-oracle-dynamic-monitoring-service.html#GUID-CF203F66-A0AD-4FBA-B68C-BD1A0CC5187C) 를 참고하시기 바랍니다.

<br>

OHS 에서는 기본적으로, `mod_dms.so` 가 활성화 되어 있고,

```sh
$ cat ./config/fmwconfig/components/OHS/worker1/admin.conf
LoadModule dms_module "${PRODUCT_HOME}/modules/mod_dms.so"
...
```

<br>

LogFormat에서 X-ORACLE-DMS-ECID Header를 Logging 하기 위한 `%E` 가 포함되어 있습니다.

```sh
$ cat ./config/fmwconfig/components/OHS/worker1/httpd.conf
LogFormat "%h %l %u %t %E \"%r\" %>s %b" common
```

<br>

사용자의 요청을 처리한 Backend Oracle WebLogic Server로 부터 다음의 HTTP Response Header(`006BXOa7PzbEoIXElvtlWJ001FXh00001Z`)를 받으면, access_log에 기록합니다.

```sh
10.73.130.101 - - [14/Feb/2025:17:42:03 +0900] 006BXOa7PzbEoIXElvtlWJ001FXh00001Z "GET /session.jsp HTTP/1.1" 200 31
```

<br>

OHS가 아닌 Apache의 경우 `mod_dms.so`가 포함되어 있지 않기 때문에, 다음 처럼 Header 값을 직접 출력하도록 합니다.

```sh
LogFormat "%h %l %u %t %{X-ORACLE-DMS-ECID}o \"%r\" %>s %b" common
```


<br><br>


# 3. References

[mod_log_config](https://httpd.apache.org/docs/2.4/ko/mod/mod_log_config.html#formats)

