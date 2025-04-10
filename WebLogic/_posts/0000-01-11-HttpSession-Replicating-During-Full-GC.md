---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebLogic] HttpSession Replicating During Full GC"
tags: [Middleware, WebLogic, WebTier, HttpSession, Clustering]
typora-root-url: ..
---

# 1. Overview

고객 시스템 인스턴스 중에 1개만 Full GC로 최소 8초 정도 Stop The World 현상을 겪는 상황이 발생할 때,

앞단 OHS 로 부터 아무런 요청이 WAS 로 들어오지 않는 현상이 발생하고 있다.

이를 분석하기 위해 정리한다.

<br>


# 2. Descriptions

## 2.1 Test environments

OHS (DynamicServerList On) - WLS (M1 ~ M4, Clustering) 와 같은 환경을 테스트계에 구성했다.

고객은, Debugging이 불가능하기에 사내 테스트 환경을 구축하여 해당 이슈가 Bug인지 Work as design 인지 구분해야 한다.

<br>

OHS 는 다음과 같은 환경

```
<IfModule weblogic_module>
  WebLogicCluster wls.local:8002,wls.local:8003,wls.local:8004,wls.local:8005
  WLIOTimeoutSecs 300
  Idempotent OFF
  DebugConfigInfo ON
  DynamicServerList ON
  ConnectTimeoutSecs 20
  ConnectRetrySecs 2
  MatchExpression *.jsp
</IfModule>
```

<br>

WLS 는 다음과 같은 환경 (고객은 더 큰 환경이지만, Primary/Secondary Pair를 이루는 WLS의 특성을 고려해 4개로 구성)

```
M1~M4 , 4개의 인스턴스 Clustering
http://wls.local/newApp/session.jsp (세션 내 count 값 증가하는 단순 페이지)
```


<br><br>


## 2.2 Gathering JVMID

원할한 분석을 위해, 각 인스턴스의 JVMID를 얻어야 한다.

curl 을 반복 호출하여, Header 에서 Set-Cookie 값을 통해 유추할 수도 있지만, 여기서는 OHS Debug plugin log에서 빠르게 얻었다.

```
Parsing JVMID '832964471!wls.local!8005!-1|-144929425!wls.local!8003!-1|1389367605!wls.local!8002!-1|-493727397!wls.local!8004!-1'

위 로그는 다음처럼 정리할 수 있다.
M1 : 1389367605
M2 : -144929425
M3 : -493727397
M4 : 832964471
```

<br>

## 2.3 Load test with Jmeter

Jmeter 의 옵션중에, `same user on each iteration` 을 비활성화하여 항상 새로운 쿠키를 만들어 요청하도록 했고,

보조적으로 `HTTP Cookie Manager`에서 `Clear cookies each iteration` 를 활성화하여 항상 쿠키를 지우도록 했다.

<br>

Jmeter로 부하를 발생시키고, M1 인스턴스를 kill -STOP \<WAS PID\> 로 정지 하였다.

Jmeter에 보조도구로 `View Results Tree` 에서 수행되는 요청들을 보면,

모든 요청들이 Set-Cookie로 항상 새로운 요청으로 들어가는것이 확인되었음에도,

OHS로 아무런 요청이 들어가지 않고 Hang 상태와 같이 멈추었다.

<br>

**[Important]**

Jmeter만 curl과 달리 문제가 되는 것은, 기본 Thread가 Single Thread처럼 동작해서 그러한 것으로 확인된다.

HTTP Request - Advanced - Implementation을 Java로, Connect,Response Timeout을 2초로 변경 시

문제가 되는 M1 인스턴스 그룹 요청시에만 Hang이 발생하고, 그 외에는 문제 없이 요청이 유입되었다.


<br><br>


## 2.4 Load test with curl

curl 은 기본적으로 Cookie 지속성이 없으므로 유용한 도구로 생각되어 활용했다.

curl을 반복적으로 호출하여, 다양한 테스트 그룹에 적합한 JSESSIONID 샘플을 구했다.

<br>

M1 (Primary) : M2 (Secondary)

```sh
$ curl -v http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
...
< Set-Cookie: JSESSIONID=pdd-xM017Xei0YyG2jt86xJoHEPA83H5q3RuqJBmZNCWrZg6SZEv!1389367605!-144929425; path=/; HttpOnly
```

<br>

M3 (Primary) : M1 (Secondary)

```sh
$ curl -v http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
...
< Set-Cookie: JSESSIONID=til-zrir7X1CDGFEi03_CD-c02p1LFMHCPUMTE5PBJcVqnbVdd-O!-493727397!1389367605; path=/; HttpOnly
```

<br>

M4 (Primary) : M3 (Secondary)

```sh
$ curl -v http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
...
< Set-Cookie: JSESSIONID=9GB-x5Jfr8vY1MHR6ZC55EuggVRIjPhXmUKGIDVNbMs0qz5yFkzS!832964471!-493727397; path=/; HttpOnly
```

<br>

M1 인스턴스를 정지시에, 위의 샘플 호출 시 어떻게 동작하는지 볼 수 있다.

```sh
M1:M2 -> curl -v -b 'JSESSIONID=pdd-xM017Xei0YyG2jt86xJoHEPA83H5q3RuqJBmZNCWrZg6SZEv!1389367605!-144929425' http://wls.local/newApp/session.jsp
M3:M1 -> curl -v -b 'JSESSIONID=til-zrir7X1CDGFEi03_CD-c02p1LFMHCPUMTE5PBJcVqnbVdd-O!-493727397!1389367605' http://wls.local/newApp/session.jsp
M4:M3 -> curl -v -b 'JSESSIONID=9GB-x5Jfr8vY1MHR6ZC55EuggVRIjPhXmUKGIDVNbMs0qz5yFkzS!832964471!-493727397' http://wls.local/newApp/session.jsp
```

<br>

M1 (Primary) : M2 (Secondary) 샘플을 호출 시, 당연히 OHS Plugin은 요청을 Primary인 M1 으로 보내려고 하나 정지되어 있으므로 Hang이 관찰된다.

```sh
$ curl -v -b 'JSESSIONID=pdd-xM017Xei0YyG2jt86xJoHEPA83H5q3RuqJBmZNCWrZg6SZEv!1389367605!-144929425' http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
> GET /newApp/session.jsp HTTP/1.1
> Host: wls.local
> User-Agent: curl/7.61.1
> Accept: */*
> Cookie: JSESSIONID=pdd-xM017Xei0YyG2jt86xJoHEPA83H5q3RuqJBmZNCWrZg6SZEv!1389367605!-144929425
>
 ... 여기서 Hang ...
```

<br>

M3 (Primary) : M1 (Secondary) 샘플을 호출 시, 세션을 업데이트해야 하는데, M1 이 정지되어 있으므로 Hang이 발생한다.

```sh
$ curl -v -b 'JSESSIONID=til-zrir7X1CDGFEi03_CD-c02p1LFMHCPUMTE5PBJcVqnbVdd-O!-493727397!1389367605' http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
> GET /newApp/session.jsp HTTP/1.1
> Host: wls.local
> User-Agent: curl/7.61.1
> Accept: */*
> Cookie: JSESSIONID=til-zrir7X1CDGFEi03_CD-c02p1LFMHCPUMTE5PBJcVqnbVdd-O!-493727397!1389367605
>
 ... 여기서 Hang ...

```

<br>

M4 (Primary) : M3 (Secondary) 샘플을 호출 시, 정지된 M1 인스턴스와 관련이 없으므로 문제 없이 호출이 된다

```sh
$ curl -v -b 'JSESSIONID=9GB-x5Jfr8vY1MHR6ZC55EuggVRIjPhXmUKGIDVNbMs0qz5yFkzS!832964471!-493727397' http://wls.local/newApp/session.jsp
*   Trying 10.65.34.108...
* TCP_NODELAY set
* Connected to wls.local (10.65.34.108) port 80 (#0)
> GET /newApp/session.jsp HTTP/1.1
> Host: wls.local
> User-Agent: curl/7.61.1
> Accept: */*
> Cookie: JSESSIONID=9GB-x5Jfr8vY1MHR6ZC55EuggVRIjPhXmUKGIDVNbMs0qz5yFkzS!832964471!-493727397
>
< HTTP/1.1 200 OK
< Date: Mon, 10 Mar 2025 06:41:24 GMT
< X-Content-Type-Options: nosniff
< Content-Length: 211
< X-ORACLE-DMS-ECID: 006BzT2ljy84uljEl38xkJ003msz00001F
< X-ORACLE-DMS-RID: 0:1
< X-XSS-Protection: 1; mode=block
< Content-Type: text/html;charset=UTF-8
<

[TEST11] so.getCnt() : 6
<br>
[TEST] session.getId() : 9GB-x5Jfr8vY1MHR6ZC55EuggVRIjPhXmUKGIDVNbMs0qz5yFkzS!832964471!-493727397!1741588763231
<br>
[TEST] system.getProperty("server.name") : M4
<br>
<br>111

* Connection #0 to host wls.local left intact
```

<br>

이 테스트 과정은, `DynamicServerList Off` 시에도 동일하게 관측된다.

이미 세션이 여러 인스턴스에 분포되어 있는 상황에서, 정지된 인스턴스에 업데이트를 하려는 경우에는 Hang이 발생을 하고,

정지된 인스턴스와 관계가 없는 세션은 업데이트에 문제가 없다.

또한, 당연히 새로운 사용자로 인해 이후에 만들어진 세션은 M1 에 만들어지지도 않고, 문제가 없다.


<br><br>


## 2.5 Outcome

고객의 사례로 보면 M1 인스턴스만 Full GC로 Stop The World가 발생하는 동안, 다른 인스턴스 모두에 유입된 요청이 없다.

고객은 M1 인스턴스의 정지로 인해, 다른 인스턴스들도 영향을 받은것으로 보고 있는데,

실제 분석을 위해 위와 같이 Debugging 이나 curl 등으로 테스트가 필요하다.

<br>

고객 시스템은 내부 사용자들 시스템으로, 오전 9시경에 모든 근무자들이 일괄적으로 로그인하고 사용하는 시스템이다.

그 특성으로 인해, 오전에 생성해둔 세션이 계속 사용되고 있고, 새로운 세션이 만들어지지 않는 것과 관련이 있는게 아닐까?

그렇다고 하더라도, 위의 테스트 결과를 보듯, 문제의 M1 인스턴스와 관련없는 세션 그룹을 갖는 경우에는 호출이 되어야 한다.

이 부분은 실제 고객 시스템에서 생성되어 있는 세션 JSESSIONID의 Primary/Secondary JVMID 확인이 필요하다.

- 요청이 처리되지 않는 건마다 JSESSIONID value를 확인해서 M1 이 아닌, M2~M4 인스턴스에 대한 요청인지

<br>

정지된 인스턴스와 관련이 없는 JVMID 그룹으로 되어 있는 세션이 있는데도, 호출이 되지 않고 Hang이 발생하는 경우를 찾아 개발팀에 Bug 진행이 필요하다는 것이다.


<br><br>



# 3. References

**08-Jan-2025 01:29:16 PM 에 만들어진 SR**
