---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] HttpSession, Cookie, JSESSIONID"
tags: [Middleware, WebLogic, Session, Cookie, JSESSIONID]
typora-root-url: ..
---


# 1. Overview

테스트와 디버그 로그를 통해 HttpSession, Cookie, JSESSIONID 를 구체적으로 공부한다.


<br><br>


# 2. Cookie-Name 테스트

## 2.1 HttpSession과 Cookie, JSESSIONID

클라이언트의 브라우저에서 사용하는 HTTP 통신은 stateless(상태 무지속)방식입니다.

stateless는 클라이언트(브라우저)의 요청(request)과 서버의 응답(response) 후에는 소켓을 끊는 단발성 통신 방식입니다.

여기서 세션이나 쿠키 등을 이용하여 서버는 신규 클라이언트와 오래된 클라이언트를 구별할 수 있습니다.

<br>

### (1). HttpSession

웹 서버는 클라이언트를 구분하기 위해 클라이언트의 PC에 구별되는 세션 ID(긴 문자열)를 생성합니다.

클라이언트가 웹 서버에 다시 요청 시, 서버는 이 세션 존재여부로 신규 유저인지, 이미 로그인한 유저인지 알 수 있습니다.

<br>

### (2). Cookie

cookie는 파일로 저장되기 때문에 멀웨어 등의 악성 프로그램으로 유출되어 피해가 생길 수 있습니다.

세션은 쿠키에 저장되는 정보들을 파일로 저장하는 대신 서버와 클라이언트의 메모리 영역에 복사합니다.

하지만 클라이언트 수만큼 세션이 메모리 공간을 차지합니다.

<br>

### (3). JSESSIONID

JSESSIONID는 WAS에서 사용되는 개념입니다.

일반적인 웹 어플리케이션은 HttpSession이나 Cookie로 클라이언트를 구별합니다.

하지만 WAS에는 이러한 웹 어플리케이션이 여러개가 존재합니다.

이 하나하나의 어플리케이션들도 클라이언트를 구별하기 위해 유니크한 JSESSIONID를 메모리에 저장하여 구별합니다.


<br><br>


## 2.2 apache에 cookie-name을 TESTSESSION으로 변경하고 cookie_detail.jsp 요청 - 1회

### (1). 웹서버의 웹로직 모듈은 WebLogicCluster의 파라메터를 확인합니다.

```bash
[debug] BaseProxy.cpp(1915): [client 192.168.56.1] weblogic: parseServerList: Socket Address hostnames 'testlinux1.com:12001,testlinux2.com:12001'
```


### (2). 첫번째 서버(testlinux1.com)가 Alive 상태인지 확인합니다.

```
[debug] BaseProxy.cpp(1979): [client 192.168.56.1] weblogic: Host extracted from serverlist is [testlinux1.com]

[debug] BaseProxy.cpp(2030): [client 192.168.56.1] weblogic: parseServerList: trying IP addr 192.168.56.2

[debug] BaseProxy.cpp(2066): [client 192.168.56.1] weblogic: parseServerList: socket and connect succeeded

[debug] BaseProxy.cpp(2087): [client 192.168.56.1] weblogic: parseServerList:  IP from socket Address [192.168.56.2]
```


### (3). 두번째 서버(testlinux2.com)가 Alive 상태인지 확인합니다.

```
[debug] BaseProxy.cpp(1979): [client 192.168.56.1] weblogic: Host extracted from serverlist is [testlinux2.com]

[debug] BaseProxy.cpp(2030): [client 192.168.56.1] weblogic: parseServerList: trying IP addr 192.168.56.3

[debug] BaseProxy.cpp(2066): [client 192.168.56.1] weblogic: parseServerList: socket and connect succeeded

[debug] BaseProxy.cpp(2087): [client 192.168.56.1] weblogic: parseServerList:  IP from socket Address [192.168.56.3]
```


### (4). 응답한 서버가 2개이므로 노드 배열(길이 2)을 생성하고 서버들을 할당합니다.

```
BaseProxy.cpp(3005): [client 192.168.56.1] weblogic: Initializing lastIndex=0 for a list of length=2

[Mon Jul 06 09:37:26 2015] [debug] BaseProxy.cpp(509): [client 192.168.56.1] weblogic: getListNode: created a new server node: id='testlinux1.com:12001,testlinux2.com:12001' server_name='testlinux1.com', port='80'
```

### (5). 첫번째 서버에 연결합니다.

```
[debug] ApacheProxy.cpp(2421): [client 192.168.56.1] weblogic: Trying a pooled connection for '192.168.56.2/12001/12001'

[debug] BaseProxy.cpp(3035): [client 192.168.56.1] weblogic: getPooledConn: found a host and port/securePort match

[debug] BaseProxy.cpp(3086): [client 192.168.56.1] weblogic: getPooledConn: No more connections in the pool for Host[192.168.56.2] Port[12001] SecurePort[12001]
```

### (6). cookie_detail.jsp 의 2453 라인에 의해 소켓 연결

```
[debug] ApacheProxy.cpp(2453): [client 192.168.56.1] weblogic: general list: trying connect to '192.168.56.2'/12001/12001 at line 2453 for '/webapp/cookie_detail.jsp'

[debug] URL.cpp(1785): [client 192.168.56.1] weblogic: URL::Connect: Connected successfully

[debug] URL.cpp(1824): [client 192.168.56.1] weblogic: SSL is not configured for this connection

[debug] URL.cpp(1844): [client 192.168.56.1] weblogic: Local Port of the socket is 51741

[debug] URL.cpp(1850): [client 192.168.56.1] weblogic: Remote Host 192.168.56.2 Remote Port 51741

[debug] ApacheProxy.cpp(2487): [client 192.168.56.1] weblogic: general list: created a new connection to '192.168.56.2'/12001 for '/webapp/cookie_detail.jsp', Local port:51741
```

### (7). 웹서버는 브라우저로부터 HTTP 헤더를 전달받아 파싱을 수행합니다.

```
[debug] BaseProxy.cpp(567): [client 192.168.56.1] weblogic: Entering method BaseProxy::sendRequest

[debug] BaseProxy.cpp(1219): [client 192.168.56.1] weblogic: Entering method BaseProxy::parse_headers
```

### (8). HTTP 헤더는 총 6개의 값으로 구성되어 있음을 확인합니다.

```
[debug] BaseProxy.cpp(1237): [client 192.168.56.1] weblogic: No of headers =6

[info] [client 192.168.56.1] weblogic: Header from client:[Host]=[testlinux1.com]

[info] [client 192.168.56.1] weblogic: Header from client:[Connection]=[keep-alive]

[info] [client 192.168.56.1] weblogic: Header from client:[Accept]=[text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8]

[client 192.168.56.1] weblogic: Header from client:[User-Agent]=[Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36]

[client 192.168.56.1] weblogic: Header from client:[Accept-Encoding]=[gzip, deflate, sdch]

[info] [client 192.168.56.1] weblogic: Header from client:[Accept-Language]=[en,ko;q=0.8,en-US;q=0.6]
```

### (9). 웹서버는 헤더 파싱을 끝내고 웹로직 서버로 헤더를 전달하기 위해 GET 방식을 사용합니다.

```
[debug] BaseProxy.cpp(1413): [client 192.168.56.1] weblogic: Exiting method BaseProxy::parse_headers

[debug] BaseProxy.cpp(577): [client 192.168.56.1] weblogic: parse_client_headers is done

[debug] BaseProxy.cpp(681): [client 192.168.56.1] weblogic: Method is GET
```

### (10). 웹 서버는 웹로직 서버로 헤더를 전달합니다.

```
[info] [client 192.168.56.1] weblogic: URL::sendHeaders(): meth='GET' file='/webapp/cookie_detail.jsp' protocol='HTTP/1.1'

[info] [client 192.168.56.1] weblogic: Header to WLS: [Host]=[testlinux1.com]

[info] [client 192.168.56.1] weblogic: Header to WLS: [Accept]=[text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8]

[info] [client 192.168.56.1] weblogic: Header to WLS: [User-Agent]=[Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36]

[info] [client 192.168.56.1] weblogic: Header to WLS: [Accept-Encoding]=[gzip, deflate, sdch]

[info] [client 192.168.56.1] weblogic: Header to WLS: [Accept-Language]=[en,ko;q=0.8,en-US;q=0.6]

[info] [client 192.168.56.1] weblogic: Header to WLS: [Connection]=[Keep-Alive]

[info] [client 192.168.56.1] weblogic: Header to WLS: [WL-Proxy-SSL]=[false]

[info] [client 192.168.56.1] weblogic: Header to WLS: [X-Forwarded-For]=[192.168.56.1]

[info] [client 192.168.56.1] weblogic: Header to WLS: [WL-Proxy-Client-IP]=[192.168.56.1]

[info] [client 192.168.56.1] weblogic: Header to WLS: [WL-Proxy-Client-Port]=[1640]

[info] [client 192.168.56.1] weblogic: Header to WLS: [X-WebLogic-KeepAliveSecs]=[30]

[info] [client 192.168.56.1] weblogic: Header to WLS: [X-WebLogic-Force-JVMID]=[unset]

[info] [client 192.168.56.1] weblogic: Header to WLS: [X-WebLogic-Request-ClusterInfo]=[true]
```

> 첫 요청이므로 JVMID가 unset 입니다.


### (11). 웹로직 서버는 헤더를 분석하고 HTTP 200 코드와 함께 웹서버에게 RESPONSE할 페이지를 생성합니다.

```
[debug] BaseProxy.cpp(766): [client 192.168.56.1] weblogic: About to call parseHeaders

[debug] Reader.cpp(221): [client 192.168.56.1] weblogic: Reader::fill(): first=0 last=0 toRead=4096

[debug] Reader.cpp(270): [client 192.168.56.1] weblogic: Reader::fill(): sysRecv returned 413

[debug] URL.cpp(842): [client 192.168.56.1] weblogic: URL::parseHeaders: CompleteStatusLine set to [HTTP/1.1 200 OK]

[debug] URL.cpp(844): [client 192.168.56.1] weblogic: URL::parseHeaders: StatusLine set to [200 OK]

[debug] URL.cpp(852): [client 192.168.56.1] weblogic: URL::parseHeaders: StatusLineWithoutStatusCode set to [OK]
```

### (12). 웹로직 서버가 만든 헤더 정보를 웹서버가 받아 파싱합니다.

```
[info] [client 192.168.56.1] weblogic: Header from WLS:[Date]=[Mon, 06 Jul 2015 00:37:26 GMT]

[info] [client 192.168.56.1] weblogic: Header from WLS:[Content-Length]=[578]

[info] [client 192.168.56.1] weblogic: Header from WLS:[Content-Type]=[text/html;charset=UTF-8]

[info] [client 192.168.56.1] weblogic: Header from WLS:[X-WebLogic-Cluster-List]=[1104478448!testlinux1.com!12001!-1|1625602300!testlinux2.com!12001!-1]

[info] [client 192.168.56.1] weblogic: Header from WLS:[X-WebLogic-JVMID]=[1104478448]

[info] [client 192.168.56.1] weblogic: Header from WLS:[Set-Cookie]=[JSESSIONID=Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5!1104478448!1625602300; path=/; HttpOnly]

[info] [client 192.168.56.1] weblogic: Header from WLS:[X-WebLogic-Cluster-Hash]=[UGYKWofLj2uHaIuW02FSaDWNmdU]
```

### (13). 헤더 파싱을 끝내고 200 OK 상태로 표현합니다.

```
[debug] URL.cpp(966): [client 192.168.56.1] weblogic: parsed all headers OK

[debug] BaseProxy.cpp(840): [client 192.168.56.1] weblogic: Exiting method BaseProxy::sendRequest

[debug] ApacheProxy.cpp(244): [client 192.168.56.1] weblogic: sendResponse() : r->status = '200'
```

### (14). 이 부분은, 가장 마지막에 접속한 서버를 표시하는 것 같습니다.

```
[debug] BaseProxy.cpp(345): [client 192.168.56.1] weblogic: Free old srvrList, id=[testlinux1.com:12001,testlinux2.com:12001], server_name=[testlinux1.com], server_port=[80]
```

### (15). 헤더에서 클러스터 목록, JVM ID를 구하고 파싱합니다.

```
[debug] BaseProxy.cpp(2191): [client 192.168.56.1] weblogic: Parsing cluster list: 1104478448!testlinux1.com!12001!-1|1625602300!testlinux2.com!12001!-1

[debug] BaseProxy.cpp(2498): [client 192.168.56.1] weblogic: parseJVMID: Parsing JVMID '1104478448!testlinux1.com!12001!-1|1625602300!testlinux2.com!12001!-1'

[debug] BaseProxy.cpp(2550): [client 192.168.56.1] weblogic: parseJVMID: Actually parsing '1104478448!testlinux1.com!12001!-1'

[debug] BaseProxy.cpp(2643): [client 192.168.56.1] weblogic: ServerInfo struct for JVMID '1104478448' populated, Server Details are: OrigHostInfo [testlinux1.com], isOrigHostInfoDNS [1], Host [192.168.56.2], Port [12001], SecurePort [0]

[debug] BaseProxy.cpp(2498): [client 192.168.56.1] weblogic: parseJVMID: Parsing JVMID '1625602300!testlinux2.com!12001!-1'

[debug] BaseProxy.cpp(2550): [client 192.168.56.1] weblogic: parseJVMID: Actually parsing '1625602300!testlinux2.com!12001!-1'

[debug] BaseProxy.cpp(2643): [client 192.168.56.1] weblogic: ServerInfo struct for JVMID '1625602300' populated, Server Details are: OrigHostInfo [testlinux2.com], isOrigHostInfoDNS [1], Host [192.168.56.3], Port [12001], SecurePort [0]
```

>testlinux1.com 의 JVM ID 는 1104478448
>
>testlinux2.com 의 JVM ID 는 1625602300


### (16). 위 파싱에 의해, 처음처럼 두개의 서버를 유지하고 있음을 알 수 있습니다.

```
[debug] BaseProxy.cpp(3005): [client 192.168.56.1] weblogic: Initializing lastIndex=0 for a list of length=2

[debug] BaseProxy.cpp(380): [client 192.168.56.1] weblogic: ### Got a new Server List of length 2 ###

[debug] BaseProxy.cpp(382): [client 192.168.56.1] weblogic: ###Response### : Srvr# [1] = [192.168.56.2:12001:0]

[debug] BaseProxy.cpp(382): [client 192.168.56.1] weblogic: ###Response### : Srvr# [2] = [192.168.56.3:12001:0]
```

### (17). 클라이언트의 헤더에 GMT(+9시간) 시간을 넣습니다.

```
[info] [client 192.168.56.1] weblogic: Hdrs to client (add):[Date]=[Mon, 06 Jul 2015 00:37:26 GMT]
```

> 이 GMT 시간은 클라이언트와 웹로직 서버가 메모리에 저장하는 세션 정보의 마지막에 포함됩니다.


### (18). 클라이언트의 헤더에 JSESSIONID 쿠키를 할당합니다.

```
[info] [client 192.168.56.1] weblogic: Hdrs to client (add):[Set-Cookie]=[JSESSIONID=Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5!1104478448!1625602300; path=/; HttpOnly]
```

> JSESSIONID 생성 규칙은 {세션 ID}!{Primary Server의 JDM IV}!{Secondary 서버의 JVM ID} 입니다.
>
> 그러므로 웹로직 서버가 클라이언트에게 만들어준 세션 ID는
>
> Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5 임을 알 수 있습니다.


### (19). cookie_detail.jsp와 연결을 끊습니다.

```
[debug] BaseProxy.cpp(3124): [client 192.168.56.1] weblogic: closeConn: pooling for '192.168.56.2/12001'

[debug] BaseProxy.cpp(3138): [client 192.168.56.1] weblogic: closeConn: pooling '0'

[debug] ap_proxy.cpp(705): [client 192.168.56.1] weblogic: request [/webapp/cookie_detail.jsp] processed successfully..................
```

## 2.3 apache에 cookie-name을 TESTSESSION으로 변경하고 cookie_detail.jsp 요청 - 2회

### (1). 같은 클라이언트(브라우저)가 다시 똑같은 페이지를 요청할 경우 웹로직 첫번째 서버는 클라이언트의 HTTP 헤더에서 사용 가능한 JSESSIONID 쿠키를 발견합니다.

```
[debug] ApacheProxy.cpp(1738): [client 192.168.56.1] weblogic: getPreferred: availcookie=[JSESSIONID=Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5!1104478448!1625602300]
```

> 이 JSESSIONID는 **단계 1.2.(15)**의 쿠키와 동일합니다.
>
> 현재 쿠키 내용을 보면, 세션 ID = Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5, Primary = 1104478448, Secondary = 1625602300 임을 알 수 있습니다.


### (2). 클라이언트는 Primary 서버로 연결되며, 쿠키로 TESTSESSION을 찾습니다. 하지만 Primary 서버와 클라이언트에는 TESTSESSION 쿠키가 없습니다. 웹로직 서버는 Primary 와 Secondary를 바꾸어 JSESSIONID 를 다시 할당합니다. 다시 할당 하는 이유는 다음 연결때는 Secondary로 가게 되기 때문입니다.

```
[info] [client 192.168.56.1] weblogic: Header from WLS:[Set-Cookie]=[JSESSIONID=Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5!1104478448; path=/; HttpOnly]

[info] [client 192.168.56.1] weblogic: Hdrs to client (add):[Set-Cookie]=[JSESSIONID=Zf5gy86ROihZsEMgEvASu-t4kwc6pYRxcU3KnwIL27XuzW6dAoW5!1625602300!1104478448; path=/; HttpOnly]
```

> 웹로직에서 쿠키를 읽었을 때, Primary 값이 현재 서버가 아니면 is not primary server 등으로 로그를 뿌린다. 이때 다시 Primary 서버를 현재 서버로 정하고, Secondary 서버를 선택하게 되는데, 랜덤으로 선택한다. 원래 Secondary는 랜덤 선택.


## 2.4 apache와 weblogic의 cookie name을 TESTSESSION으로 동일 설정

### (1). 첫 접속 시 웹로직은 TESTSESSION으로 쿠키를 할당합니다.

### (2). 두번째 접속 시 클라이언트가 요청하는 TESTSESSION은 웹로직과 동일하므로 쿠키를 발견하고, 파싱하여 정보를 얻을 수 있습니다.

```
[debug] ApacheProxy.cpp(1738): [client 192.168.56.1] weblogic: getPreferred: availcookie=[TESTSESSION=Sfxh2Z5GFEaGKSt4fH_-YsWru2wFdHzmmZVJV1xwMwBQRT4Mp-EQ!1104478448!1625602300]

[debug] ApacheProxy.cpp(1785): [client 192.168.56.1] weblogic: Found cookie from cookie header: TESTSESSION=Sfxh2Z5GFEaGKSt4fH_-YsWru2wFdHzmmZVJV1xwMwBQRT4Mp-EQ!1104478448!1625602300

[debug] BaseProxy.cpp(1464): [client 192.168.56.1] weblogic: Parsing cookie TESTSESSION=Sfxh2Z5GFEaGKSt4fH_-YsWru2wFdHzmmZVJV1xwMwBQRT4Mp-EQ!1104478448!1625602300
```

### (3). 쿠키에서 세션 타임아웃 방지를 위한 시간만 갱신합니다.

```
[info] [client 192.168.56.1] weblogic: Hdrs to client (add):[Date]=[Mon, 06 Jul 2015 05:32:18 GMT]
```

## 2.5 apache cookie name은 TESTSESSION2, wls cookie name은 TESTSESSION1 일 때

> 단계 1.2 의 테스트와 동일한 결과를 보여줍니다. 요청하는 쿠키명과 배급되는 쿠키명이 다르기 때문입니다.


이로써 쿠키로 사용자(브라우저)가 신규 접속인지, 아니라면 가지고 있는 쿠키를 분석하여 웹 어플리케이션이 원하는 정보인지를 알 수 있습니다.


<br><br>


# 3. JSESSION ID 테스트

## 2.1 같은 cookie 를 발급하는 cookie_detail.jsp 호출

> (1) webapp1/cookie_detail.jsp 호출 -> count = 1
>
> (2) webapp1/cookie_detail.jsp 호출 -> count = 2
>
> (3) webapp2/cookie_detail.jsp 호출 -> count = 1
>
> (4) webapp1/cookie_detail.jsp 호출 -> count = 1
>
> webapp1과 webapp2가 동일한 쿠키명을 사용하고 있어, 다른 어플리케이션이 세션을 덮어씌워버리기 때문에 1씩 증가되는 count 변수 또한 초기화 됩니다.

<br>

사용자의 세션 정보가 필요한 어플리케이션이 다수 일때, 어플리케이션들의 쿠키명이 동일하다면 이전의 정보가 제거 됩니다. 이를 위해 어플리케이션 별로 쿠키명이 달라야 합니다.


<br><br>


# 4. 세션 공유 테스트

## 4.1 도메인 단위

여러 서브 도메인에서 하나의 어플리케이션 세션을 weblogic.xml 설정을 통해 공유 할 수 있습니다.

```weblogic.xml
<weblogic-web-app>
     <session-descriptor>
          <cookie-name>SUBSESSION</cookie-name>
          <cookie-domain>.main.com</cookie-domain>
     </session-descriptor>
</weblogic-web-app>
```

```/etc/hosts
192.168.56.2 sub1.main.com sub2.main.com
```

> 위의 설정은 sub1.main.com과 sub2.main.com 에서 세션 공유가 됩니다.
>
> cookie-domain에는 도메인 명 외에도, ip주소(.168.56.2)로 설정하여 세션 공유할 수 있습니다.
>
> 점(.)이 최소 2개가 있어야 합니다. (.co.kr 은 되지 않습니다.)

<br>


## 4.2 어플리케이션 단위

여러 어플리케이션을 하나의 인스턴스에서 세션을 공유할 때는 ear 구조가 되어야 합니다.

<br>

### (1). ear 구조

```
/earapp
	webapp1 (단계 3.1의 어플리케이션)
	webapp2 (단계 3.1의 어플리케이션)
	META-INF
		 application.xml
```

```application.xml
<application>
        <display-name>earapp</display-name>
        <module>
                <web>
                        <web-uri>webapp1</web-uri>
                        <context-root>/webapp1</context-root>
                </web>
        </module>
​
        <module>
                <web>
                        <web-uri>webapp2</web-uri>
                        <context-root>/webapp2</context-root>
                </web>
        </module>
</application>
```

```weblogic.xml
<weblogic-application>
        <session-descriptor>
                <cookie-path>/</cookie-path>
                <sharing-enabled>true</sharing-enabled>
        </session-descriptor>
</weblogic-application>
```

ear패키징으로 인해 webapp1과 webapp2가 묶여있습니다.

webapp1과 webapp2 둘다 생성하는 쿠키 이름은 JSESSIONID 입니다.

<sharing-enabled> 옵션으로 두 어플리케이션은 JSESSIONID를 공유합니다.
