---
date: 2022-12-06 08:53:52 +0900
layout: post
title: "[OHS] Oracle HTTP Server 12cR2 Configurations"
tags: [OracleHTTPServer, OHS, Config]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 12cR2 Configurations



# 2. Performance

Performance에 직접적으로 연관된 설정을 살펴본다.



## 2.1 MPM

ohs.plugins.nodemanager.properties 파일에서 변경한다.

```ohs.plugins.nodemanager.properties
#   mpm                   whether to use prefork or worker or event MPM
#       valid values:     "prefork" and "worker" and "event"
#       default:          "event"

mpm = worker
```



httpd.conf 파일에서 변경한다. (예시로 mpm_worker 방식)

```httpd.conf
<IfModule mpm_worker_module>
    StartServers              1
    ServerLimit               4
    MinSpareThreads         256
    MaxSpareThreads         768
    ThreadsPerChild         256
    ThreadLimit             256
    MaxRequestWorkers      1024
    MaxConnectionsPerChild    0
    Mutex fcntl:${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs
</IfModule>
```



## 2.2 Keep Alive

Client 와 Web 간의 Keepalive는 httpd.conf에 설정한다.

```httpd.conf
KeepAlive On
KeepAliveTimeout 5
```



Web-ProxyPlugin과 WAS는 [6. Proxy Plugin](#h-6-proxy-plugin) 과 같이 설정한다.

```mod_wl_ohs.conf
     KeepAliveEnabled ON
     KeepAliveSecs 5
```



# 3. Security

## 3.1 HTTP Method

```httpd.conf
DocumentRoot "..."
<Directory "...">
	...
    <LimitExcept POST GET>
       Require all denied
    </LimitExcept>
</Directory>
```



Require method 지시어로 올바른 동작이 되지 않아 LimitExcept 지시어를 사용하였다.



## 3.2 Options

```httpd.conf
DocumentRoot "..."
<Directory "...">
	...
    Options None
</Directory>
```



# 4. Logging

%D LogFormat을 추가하였다.

```httpd.conf
LogFormat "%h %l %u %t %E \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" (%D)" combined
```



access_log Rotation (KST 00~24)

```httpd.conf
CustomLog "||${PRODUCT_HOME}/bin/odl_rotatelogs -u:32400 ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/access_log 86400" combined
```



error_log Rotation (KST 00~24)

```httpd.conf
ErrorLog "||${PRODUCT_HOME}/bin/odl_rotatelogs -u:32400 ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/error_log 86400"

...
OraLogMode apache
...
```



# 5. Monitoring

## 5.1 server-status

```
<Location /server-status>
    SetHandler server-status
    Require ip 127
</Location>
```



/server-status 페이지를 접근하는 Client IP가 127 으로 시작하는 경우에만 허가한다.



## 5.2 DebugConfigInfo

Proxy Plugin에서 다음의 옵션을 활성화 할 경우, Query String `__WebLogicBridgeConfig` 으로 접근 할 수 있다.

```mod_wl_ohs.conf
DebugConfigInfo On
```



[공식 문서](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-2C0354F4-218A-4EBF-8BFD-B3140F7FE736)에서는, `keep this parameter turned OFF in production systems` 으로 권장하고 있다.

혹은, 다음과 같이 설정하여 특정 접근만 허용할 수 있으므로 Debug 시에는 활용 할 수 있겠다.

```mod_wl_ohs.conf
<Location /serverSide>
     WLSRequest On

     <If "%{QUERY_STRING} =~ /__WebLogicBridgeConfig/">
          Require ip 127
     </If>
</Location>
```





# 6. Proxy Plugin

```mod_wl_ohs.conf
<IfModule weblogic_module>
     WebLogicCluster wls.local:8003,wls.local:8004
     ConnectRetrySecs 1
     WLSocketTimeoutSecs 2
     ConnectTimeoutSecs 5
     MaxSkipTime 10
     WLIOTimeoutSecs 300
     DynamicServerList OFF
     Idempotent OFF
     FileCaching OFF
     KeepAliveEnabled ON
     KeepAliveSecs 5
     WLCookieName JSESSIONID

     MatchExpression *.jsp
</IfModule>

<Location /serverSide>
     WLSRequest On
</Location>
```



/serverSide 호출 시 WLS으로 응답한다.
