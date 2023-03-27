---
date: 2023-03-27 08:46:20 +0900
layout: post
title: "[WebServer/WLPlugin] WebLogic Proxy Plugin 12cR2의 Failover 동작"
tags: [Apache, OHS, Plugin, wlplugin, GET, POST, Failover, Idempotent]
typora-root-url: ..
---

# 1. 개요

WebLogic Proxy Plugin 12cR2에서 Failover 를 처리하는 방법에 대해서 다양하게 살펴본다.



# 2. 설명

사용자의 GET/POST 요청의 처리 도중 Failed 시에 다른 Available Instance로 Failover를 위해 필요한 옵션은

* FileCaching
* Idempotent
* WLRetryOnTimeout
* WLRetryAfterDroppedConnection
* WLServerInitiatedFailover



# 3. GET Method

GET Method 방식에서 Failover시에는, 다음의 옵션으로 구성되어 있어야 한다.

```
Idempotent ON
WLRetryOnTimeout [ALL 또는 IDEMPOTENT]
WLRetryAfterDroppedConnection [ALL 또는 IDEMPOTENT]
WLServerInitiatedFailover [ALL 또는 IDEMPOTENT]
```

[Idempotent 설명](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-C25D4368-26CE-4CA3-8433-F6BD99CF4BF9)

[WLRetryOnTimeout 설명](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-57E6B538-D013-4A47-884A-DECD267F9EBF)

[WLRetryAfterDroppedConnection 설명](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-46CA508A-25AD-4C8A-ACA0-A6746AFD7FDD)

[WLServerInitiatedFailover 설명](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-8B1817F7-F7D2-454D-8FE6-8C5FF5705F8B)



ALL : GET/POST 모두 Failover

IDEMPOTENT : GET method만 Failover, POST method는 [RFC 9110 - HTTP Method Registration](https://www.rfc-editor.org/rfc/rfc9110.html#name-method-registration)에 따라 Idemponent Method가 아니다.

NONE : Failover 하지 않음



모든 옵션이 ALL 또는 IDEMPOTENT로 정의되어야 GET Method의 Failover 구현이 가능하다.



# 4. POST Method

POST Method 방식에서 Failover시에는, 다음의 옵션으로 구성되어 있어야 한다.

```
FileCaching ON
Idempotent ON
WLRetryOnTimeout ALL
WLRetryAfterDroppedConnectionALL
WLServerInitiatedFailover ALL
```



위에서 언급하였는데, POST는 기본적으로 Idempotent Method가 아니다.

또한, 실제 Field에서도 이중 거래와 같은 문제를 피하기 위해 POST는 Failover되지 않도록 설정한다.

HTTP Spec 기본 사양에도 불구하고 WL Proxy Plugin에서 POST Method 또한 Failover 가능하도록 구현이 되어 있다.



## 4.1 Do Small POST Failover

POST Method의 Failover 과정을 Debug log(`LogLevel debug`)로 살펴보면 좀 더 이해하기 쉽다.



POST Size가 `2048 Bytes` 보다 작고, `FileCaching OFF 또는 ON` 인 경우, Failover가 수행된다.

POST size가 `2048 bytes` 보다 작은 요청일 때, in memory 로 Post data를 읽어 들인다.

```
Going to get the post data of size=14 clength=0
Post data length: 14 (in memory)
```



연결된 Instance에서 HTTP 503 Status Line을 받았을 때,

```
sendResponse() : r->status = '503'
Marking *.*.*.*:8002 as unavailable for new requests
*******Exception type [FAILOVER_REQUIRED] (Service Unavailable) raised at line 244 of BaseProxy.cpp
got exception in sendResponse phase: FAILOVER_REQUIRED [line 244 of BaseProxy.cpp]: Service Unavailable at line 682
```



POST Size가 작은 경우에는, in memory로 수행하기 때문에 재전송이 가능하다.

결국 어떠한 경우에든 Failover 수행 된다.

```
ap_proxy: trying POST /PostDataTest/recv.jsp at backend host *.*.*.*/8002, client *.*.*.*/55308, total tries 6; got exception 'FAILOVER_REQUIRED [line 244 of BaseProxy.cpp]: Service Unavailable'; state: reading status line or response headers from WLS; failing over
```



## 4.2 Do Big POST Failover

POST Size가 `2048 Bytes` 보다 크고, `FileCaching ON` 인 경우, Failover가 수행된다.

POST size가 `2048 bytes` 보다 큰 요청일 때, Disk로 Post data를 읽어 들인다.

```
Going to get the post data of size=6879
getWLFilePath: Complete File name = [/tmp/_wl_proxy/_post_928399_0]
Read 6879 of expected 6879 bytes of request body
```



이후 Log는 상동이며, POST가 Idemponent하지 않지만 Plugin에서 이를 가능하도록 구현하였기 때문에 Disk에 임시로 기록해둔 POST Data를 재전송하여 Failover를 수행한다.



`FileCaching OFF` 인 경우에는 Big Size의 POST Data는 어떤 경우에도 Failover 할 수 없다.

어떠한 경우에라는 것은, HTTP 503 Service Unavailable 또는 READ_TIMEOUT 등등 모든 경우를 뜻한다.



# 5. References

[General Parameters for Web Server Plug-Ins](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/develop-plugin/plugin_params.html#GUID-08B84046-0EF9-4A21-B1A3-4618A3D4E87A)

12c proxy plug-in에서 HTTP request의 retry 여부 설정 (Doc ID 2785265.1)

[RFC 9110 HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
