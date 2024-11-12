---
date: 2023-06-23 08:57:06 +0900
layout: post
title: "[WebTier/Apache] KeepAlive"
tags: [WebTier, OHS, Apache, Common, WLPlugin, Plugin]
typora-root-url: ..
---

# 1. Overview

Client 의 요청이 Backend WAS Server에 도달하는 과정에서 KeepAlive가 HTTP Connection 의 흐름에 어떤 영향을 주는지 살펴본다.


<br><br>


# 2. Descriptions

Chrome Browser(Client) 로 요청을 받는 OHS WEB과 WEB내의 WLPluign, 그리고 Backend Weblogic Server까지 흐름을 `netstat` 명령과 Plugin debug log로 살펴본다.


<br><br>


## 2.1 Port간의 ESTABLISHED

요청이 인입되면, 각 Perspective 별로 어떻게 Port가 ESTABLISHED 하는지 간단히 살펴본다.


<br><br>


### 2.1.1 Environments

환경은 다음과 같이 준비하였고,

```
OS, RHEL 8.7
Client, Chrome Browser
WEB, OHS 12cR2 (including mod_wl_ohs.so)
WAS, WLS 12cR2
```


KeepAlive는 다음과 같이 설정하였다.

```
httpd.conf - KeepAliveTimeout 120 (Seconds)
mod_wl_ohs.conf - KeepAliveSecs 10 (Seconds)
WAS - Default 30 (Seconds)
```


mpm_worker를 다음과 같이 수정하여, httpd process를 축소했고, 그로 인해 Monitoring해야 하는 Port가 줄어들어 분석에 도움이 된다.

```
<IfModule mpm_worker_module>
    StartServers              1
    ServerLimit               1
```


cgi daemon socket을 비활성화하여, 분석에 도움이 된다.

```
#LoadModule cgid_module "${PRODUCT_HOME}/modules/mod_cgid.so"
```

<br>


### 2.1.2 Client Perspective

Chrome에서 요청을 인입하고, 요청을 처리하기 위한 Process에서 Socket Connection을 맺게 될 텐데, 그 과정을 추적하며 정리해보기로 한다.

<br>

`http://wls.local:1080/SessionApp/session.jsp?Client-Perspective` WEB으로 호출 시 Windows netstat 을 통해 ESTABLISHED 와 연관된 Process를 보면,

```
> netstat -ano | findstr 1080
  TCP    10.8.125.203:52146     10.65.34.245:1080      ESTABLISHED     28788
  TCP    10.8.125.203:52147     10.65.34.245:1080      ESTABLISHED     28788
  TCP    10.8.125.203:52148     10.65.34.245:1080      ESTABLISHED     28788
```


```
> tasklist /fi "pid eq 28788"

이미지 이름                    PID 세션 이름              세션#  메모리 사용
========================= ======== ================ =========== ============
chrome.exe                   28788 Console                    1     46,012 K
```


Chrome에서 ESTABLISHED 3개가 확인된다.

왜 3개가 생성되는지는 모르겠다.

Client가 WEB 과 ESTABLISHED 하기 위해 어떤 Dynamic Port를 사용하는지는 WLPlugin Log를 살펴야 한다.

__아래에서 확인 결과 52146을 사용했다__

<br>

> Client Windows IP : 10.8.120.59
>
> Server Box IP : 10.65.34.245 or wls.local Hostname

<br>


### 2.1.3 WEB Perspective

다음의 Script를 준비하고,

```sh
CLIENT_IP=10.8.125.203
WEB_PORT=1080
WEB_ADM_PORT=10099
WAS_PORT=8002
ACCESS_LOG=/sw/webtier/12cR2/domains/base_domain/servers/worker1/logs/access_log

echo "Current Date :    $(date)"
grep "GET" ${ACCESS_LOG} | tail -1
echo -e "\n"

echo "# CLIENT - WEB (WEB perspective)"
CLIENT_TO_WEB=$(sudo netstat -anp | grep "httpd" | grep "${CLIENT_IP}")
echo "--------------------"
echo "${CLIENT_TO_WEB}"
echo "--------------------"
echo -e "\n\n\n"

echo "# WEB(PLUGIN) - WAS (PLUGIN perspective)"
WEB_TO_WAS=$(sudo netstat -anp | grep "httpd" | grep -v "LISTEN" | grep -v "${WEB_ADM_PORT}")
echo "--------------------"
echo "${WEB_TO_WAS}"
echo "--------------------"
echo -e "\n\n\n"

echo "# WAS (WAS perspective)"
WAS_ENDPOINT=$(sudo netstat -anp | grep "${WAS_PORT}" | grep -v "LISTEN")
echo "--------------------"
echo "${WAS_ENDPOINT}"
echo "--------------------"
```


Client Perspective에서 확인한 Dynamic Port는 Script 결과로도 알 수 있다.

<br>

사용자 요청이 인입되었을 때, 1초 Data를 수집해보면

```sh
$ watch -n 1 /tmp/monitor.sh
Every 1.0s: /tmp/monitor.sh

Current Date :    Thu Jun 29 10:30:49 KST 2023
10.8.125.203 - - [29/Jun/2023:10:30:28 +0900] 005zne_CKXtEoIXElvtlWJ00FAQb0000DU "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88


# CLIENT - WEB (WEB perspective)
--------------------
tcp        0      0 10.65.34.245:1080       10.8.125.203:52146      ESTABLISHED 3974823/httpd
--------------------




# WEB(PLUGIN) - WAS (PLUGIN perspective)
--------------------
tcp        0      0 10.65.34.245:64654      10.65.34.245:8002       ESTABLISHED 3974823/httpd
tcp        0      0 10.65.34.245:1080       10.8.125.203:52146      ESTABLISHED 3974823/httpd
--------------------




# WAS (WAS perspective)
--------------------
tcp        0      0 10.65.34.245:64654      10.65.34.245:8002       ESTABLISHED 3974823/httpd
tcp        0      0 10.65.34.245:8002       10.65.34.245:64654      ESTABLISHED 1130448/java
--------------------
```


Client의 52146 Port가 OHS의 1080 Port와 ESTABLISHED 되었다.

WLPlugin은 64654 Port로 WAS 8002와 ESTABLISHED 되었다.


<br><br>


### 2.1.4 OHS/Plugin Perspective

`?Client-Perspective` Query String으로 호출 했기 때문에, Debug log를 검색하기 수월하다.

<br>

Access Log에서 요청 확인

```
10.8.125.203 - - [29/Jun/2023:10:30:28 +0900] 005zne_CKXtEoIXElvtlWJ00FAQb0000DU "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88
```


일부 불필요한 Text 를 제외하고 보면,

```
[Thu Jun 29 10:30:28.210120 2023] ... [client 10.8.125.203:52146] ... ================New Request: [GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1] =================
                                  
[Thu Jun 29 10:30:28.211024 2023] ... [client 10.8.125.203:52146] ... Local Port of the socket is 64654
[Thu Jun 29 10:30:28.211040 2023] ... [client 10.8.125.203:52146] ... Remote Host 10.65.34.245 Remote Port 64654
[Thu Jun 29 10:30:28.211063 2023] ... [client 10.8.125.203:52146] ... created a new connection to preferred server '10.65.34.245/8002' for '/SessionApp/session.jsp?Client-Perspective', Local port:64654
```


이미 Log Text에도 Client IP와 Dynamic Port 52146이 확인된다.

WLPlugin은 WAS와 연결하기 위해 내부적으로 64654 Port에 연결됐다.


<br><br>


## 2.2 KeepAlive에 따른 Port 변화

앞서 httpd.conf KeepAlive를 120초로 설정하였다.

120초간 위에서 확인된 52146 Port가 ESTABLISHED로 유지되는지 확인한다.

> Test 과정에서 소요되는 시간 상, Port Number는 달라질 수 있다.


```
[Thu Jun 29 10:31:28.534496 2023] ... [client 10.8.125.203:52146] ... ================New Request: [GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1] =================

[Thu Jun 29 10:31:28.535896 2023] ... [client 10.8.125.203:52146] ... Local Port of the socket is 51384
[Thu Jun 29 10:31:28.535914 2023] ... [client 10.8.125.203:52146] ... Remote Host 10.65.34.245 Remote Port 51384
[Thu Jun 29 10:31:28.535936 2023] ... [client 10.8.125.203:52146] ... created a new connection to preferred server '10.65.34.245/8002' for '/SessionApp/session.jsp?Client-Perspective', Local port:51384
```


충분히 1분이라는 시간 뒤에 새로고침을 했음에도, OHS의 KeepAlive 에 의해 Client와 ESTABLISHED 되어 있는 52146 Port가 살아있다.

<br>

그리고, mod_wl_ohs.conf KeepAliveSecs 는 10초이다.

WLPlugin의 KeepAlive는 10초로 짧기 때문에, 그 사이에 64654 에서 51384 로 변경되었다.


<br><br>


## 2.3 KeepAlive에 따른 Port 변화 #2

WLPlugin에 KeepAliveSecs 60 로 설정하여,

OHS(120) - WLPlugin(60) - WLS(30) 의 환경을 구성하였다.

<br>

다음 시점에 호출을 했고,

```
10.8.125.203 - - [29/Jun/2023:10:48:47 +0900] 005znfaj0ApEoIXElvtlWJ00FYvc000003 "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88
```


```
[Thu Jun 29 10:48:47.820999 2023] ... [client 10.8.125.203:52522]  ================New Request: [GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1] =================

[Thu Jun 29 10:48:47.826695 2023] ... [client 10.8.125.203:52522] ... Local Port of the socket is 54084
[Thu Jun 29 10:48:47.826707 2023] ... [client 10.8.125.203:52522] ... Remote Host 10.65.34.245 Remote Port 54084
[Thu Jun 29 10:48:47.826724 2023] ... [client 10.8.125.203:52522] ... created a new connection to preferred server '10.65.34.245/8002' for '/SessionApp/session.jsp?Client-Perspective', Local port:54084
```


Client 와 OHS 간에는 52522 Port가 사용되고,

WLPlugin과 WLS간에는 54084 Port가 사용된다.

<br>

1분이 채 안되는 시점 재호출을 하였고,

```
10.8.125.203 - - [29/Jun/2023:10:49:43 +0900] 005znfe5G9xEoIXElvtlWJ00FYvc000006 "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88
```


```
[Thu Jun 29 10:49:43.985232 2023] ... [client 10.8.125.203:52522] ================New Request: [GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1] =================

[Thu Jun 29 10:49:43.986780 2023] ... [client 10.8.125.203:52522] Local Port of the socket is 48970
[Thu Jun 29 10:49:43.986797 2023] ... [client 10.8.125.203:52522] Remote Host 10.65.34.245 Remote Port 48970
[Thu Jun 29 10:49:43.986824 2023] ... [client 10.8.125.203:52522] created a new connection to preferred server '10.65.34.245/8002' for '/SessionApp/session.jsp?Client-Perspective', Local port:48970
```


Client와 OHS 간에는 여전히 52522 Port가 유지되고,

WLS의 Default 30초의 KeepAliveTimeout으로 인해, 48970 Port가 새로 생성되었다.

<br>

이러한 Test를 추가적으로 한 이유로는,

WLPlugin 에서 인지하고 있는 Port로 송/수신을 시도하지만, WLS에서는 Port가 유실될 경우

어떤 Exception이 발생하는지 보려고 했지만 이를 사전에 WLPlugin의 Code level에서 처리되는 것 같다.


<br><br>


# 3. Outcome

Multi Tier 간에서 KeepAlive 의 흐름을 파악했다,

다음에는 Java standalone program 간에는 어떤 Issue가 생기는지까지 살펴보도록 한다.

<br>

이번 Test에서는 별다른 Issue가 없었지만, 일반적으로 권장되는 것은

Client < WEB < WLS 와 같은 순으로 KeepAliveTimeout을 조정해야 된다.


<br><br>


# 4. References

없음
