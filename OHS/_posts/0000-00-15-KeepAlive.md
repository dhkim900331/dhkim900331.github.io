---
date: 2023-06-23 08:57:06 +0900
layout: post
title: "[OHS/Common] KeepAlive"
tags: [OracleHTTPServer, OHS, Apache, Common, WLPlugin, Plugin]
typora-root-url: ..
---

# 1. Overview

Client 의 요청이 Backend WAS Server에 도달하는 과정에서 KeepAlive가 HTTP Connection 의 흐름에 어떤 영향을 주는지 살펴본다.





# 2. Descriptions

Chrome Browser(Client) 로 요청을 받는 OHS WEB과 WEB내의 WLPluign, 그리고 Backend Weblogic Server까지 흐름을 `netstat` 명령과 Plugin debug log로 살펴본다.





## 2.1 Port간의 ESTABLISHED

요청이 인입되면, 각 Perspective 별로 어떻게 Port가 ESTABLISHED 하는지 간단히 살펴본다.



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





### 2.1.2 Client Perspective

Chrome에서 요청을 인입하고, 요청을 처리하기 위한 Process에서 Socket Connection을 맺게 될 텐데, 그 과정을 추적하며 정리해보기로 한다.



`http://wls.local:1080/SessionApp/session.jsp?Client-Perspective` 호출 시 Windows netstat 을 통해 ESTABLISHED 와 연관된 Process를 보면,

```
>netstat -ano | findstr 1080
  TCP    10.8.120.59:61543      10.65.34.245:1080      ESTABLISHED     23604
  TCP    10.8.120.59:61544      10.65.34.245:1080      ESTABLISHED     23604
  TCP    10.8.120.59:61545      10.65.34.245:1080      ESTABLISHED     23604
```



```
>tasklist /fi "pid eq 23604"

이미지 이름                    PID 세션 이름              세션#  메모리 사용
========================= ======== ================ =========== ============
chrome.exe                   23604 Console                    1     52,828 K
```



Chrome에서 ESTABLISHED 3개가 확인된다.

왜 3개가 생성되는지는 모르겠지만, 어떤 Dynamic port를 쓰는지는 WLPlugin Log를 살펴야 한다.

__아래에서 확인 결과 61543을 사용했다__



> Client Windows IP : 10.8.120.59
>
> Server Box IP : 10.65.34.245 or wls.local Hostname





### 2.1.3 WEB Perspective

다음의 Script를 준비하고,

```sh
CLIENT_IP=10.8.120.59
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



사용자 요청이 인입되었을 때, 1초 Data를 수집해보면

```sh
$ watch -n 1 /tmp/monitor.sh

...


Current Date :    Thu Jun 22 17:46:12 KST 2023
10.8.120.59 - - [22/Jun/2023:17:46:02 +0900] 005zfFe1kr3EoIXElvtlWJ008i6i0000DM "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88


# CLIENT - WEB (WEB perspective)
--------------------
tcp        0      0 10.65.34.245:1080       10.8.120.59:61543       ESTABLISHED 2285998/httpd
--------------------




# WEB(PLUGIN) - WAS (PLUGIN perspective)
--------------------
tcp        0      0 10.65.34.245:9690       10.65.34.245:8002       ESTABLISHED 2285998/httpd
tcp        0      0 10.65.34.245:1080       10.8.120.59:61543       ESTABLISHED 2285998/httpd
--------------------




# WAS (WAS perspective)
--------------------
tcp        0      0 10.65.34.245:9690       10.65.34.245:8002       ESTABLISHED 2285998/httpd
tcp        0      0 10.65.34.245:8002       10.65.34.245:9690       ESTABLISHED 1130448/java
tcp        0      0 10.65.34.245:8002       10.65.34.245:33128      ESTABLISHED 1130448/java
tcp        0      0 10.65.34.245:33128      10.65.34.245:8002       ESTABLISHED 2307513/java
```



Client 61543 Port는 OHS의 1080 Port와 ESTABLISHED 되었다.

WLS 8002 Port는 WLPlugin 9690 Port와 ESTABLISHED 되었다.





### 2.1.4 OHS/Plugin Perspective

`?Client-Perspective` Query String으로 호출 했기 때문에, Debug log를 검색하기 수월하다.



Access Log에서 요청 확인

```
10.8.120.59 - - [22/Jun/2023:17:11:49 +0900] 005zfDjdLDNEoIXElvtlWJ008i6i0000CI "GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1" 200 88
```



일부 불필요한 Text 를 제외하고 보면,

```
[Thu Jun 22 17:46:02.485732 2023] ... [client 10.8.120.59:61543] ================New Request: [GET /SessionApp/session.jsp?Client-Perspective HTTP/1.1] =================
                                                                 
[Thu Jun 22 17:46:02.486690 2023] ... [client 10.8.120.59:61028] Local Port of the socket is 9690
[Thu Jun 22 17:46:02.486703 2023] ... [client 10.8.120.59:61028] Remote Host 10.65.34.245 Remote Port 9690
[Thu Jun 22 17:46:02.486721 2023] ... [client 10.8.120.59:61028] created a new connection to preferred server '10.65.34.245/8002' for '/SessionApp/session.jsp?Client-Perspective', Local port:9690
                                                                 
[Thu Jun 22 17:46:02.486793 2023] ... [client 10.8.120.59:61028] Header from client:[Connection]=[keep-alive]
```



이미 Log Text에도 Client IP와 Dynamic Port 61028 이 확인된다.

WLPlugin은 WAS와 연결하기 위해 내부적으로 34028 Port를 지정하여 사용하는 것이 확인된다.





## 2.2 KeepAlive에 따른 Port 변화

앞서 httpd.conf KeepAlive를 120초로 설정하였다.

120초간 위에서 확인된 61028 Port가 ESTABLISHED로 유지되는지 확인한다.

> Test 과정에서 소요되는 시간 상, Port Number는 달라질 수 있다.



그리고, mod_wl_ohs.conf KeepAlive를 10초로 설정하였다.

Plugin 관점에서, 최소 10초동안 ESTABLISHED로 유지되는지 확인한다.





### 2.2.1 OHS KeepAlive

요청 시 Timeout이 넘지 않는 동안은 Port변화 없는지 확인





### 2.2.2 Plugin KeepAlive

