---
date: 2022-10-06 17:15:38 +0900
layout: post
title: "[WebServer/Apache] mod_proxy의 ProxyErrorOverride"
tags: [Apache, ProxyErrorOverride, ErrorDocument, mod_proxy]
typora-root-url: ..
---

# 1. 개요

Apache에서 Back-end Server에서 return 받은 Error code를 다루어 보자.



# 2. Tomcat의 Error Page

여기서 말하는 Back-end Server로 Tomcat을 사용하고,

Tomcat에서 발생하는 Error Code는 다음과 같이 자체 처리할 수 있다.



```xml
<web-app>
  <error-page>
    <error-code>404</error-code>
    <location>/error.jsp</location>
  </error-page>
 <error-page>
    <error-code>500</error-code>
    <location>/error.jsp</location>
  </error-page>
</web-app>
```



Tomcat 어플리케이션 내에서 발생한 HTTP Code 404와 500은 error.jsp 를 호출한다.



# 3. Apache의 Error Document

Apache WEB에서는 다음의 설정을 한다.



```httpd.conf
ErrorDocument 404 /error.html
ErrorDocument 500 /error.html
ErrorDocument 502 /error.html
ErrorDocument 503 /error.html
```

순수게, 위 옵션만으로 기동되는 Apache의 경우 404~503 Code는 Apache/htdocs/error.html 을 호출한다.



# 4. WEB/WAS Tier 에서의 Error Handling

## 4.1 ProxyErrorOverride Off

아래의 설정은 Apache WEB - Tomcat WAS 구조에서 흔히 사용한다.

```httpd.conf
ErrorDocument 404 /error.html
ErrorDocument 500 /error.html
ErrorDocument 502 /error.html
ErrorDocument 503 /error.html

ProxyPassMatch ^(/.*\.html)$ !
ProxyErrorOverride Off
ProxyPass        /      http://192.168.56.2:8081/
ProxyPassReverse /      http://192.168.56.2:8081/
```

`http://192.168.56.2:8081` 은 Back-end Tomcat 이다.

`ProxyErrorOverride Off` 옵션으로 인하여 Tomcat에서 발생한 HTTP Error Code는 Apache 까지 도달하지만

Apache 에서 해석하지 않아 Apache의 error.html을 호출하지 않는다.



Apache 에 없는 NoExistPage를 호출해 보면,

```sh
$ curl -v $(hostname -i):80/NoExistPage
* About to connect() to 192.168.56.2 port 80 (#0)
*   Trying 192.168.56.2...
* Connected to 192.168.56.2 (192.168.56.2) port 80 (#0)
> GET /NoExistPage HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 192.168.56.2
> Accept: */*
>
< HTTP/1.1 404
< Date: Tue, 11 Oct 2022 01:39:49 GMT
< Server: Apache
< Content-Type: text/html;charset=ISO-8859-1
< Content-Length: 13
< Set-Cookie: SCOUTER=z269a2bov57hva; Max-Age=2147483647; Expires=Sun, 29-Oct-2090 04:53:56 GMT; Path=/
< Set-Cookie: SCOUTER=x1rrsg9iei3mls; Max-Age=2147483647; Expires=Sun, 29-Oct-2090 04:53:56 GMT; Path=/
< Set-Cookie: JSESSIONID=D156EF815B53F401D74189ACC6D9E14A.tomcat_8.5.82; Path=/; HttpOnly
<
tomcat error
```

HTTP Status Code 404는 Apache 까지 전달되지만, Contents는 Tomcat의 Error page가 보여진다.



## 4.2 ProxyErrorOverride On

ProxyErrorOverride On 으로 변경 후,

```httpd.conf
ErrorDocument 404 /error.html
ErrorDocument 500 /error.html
ErrorDocument 502 /error.html
ErrorDocument 503 /error.html

ProxyPassMatch ^(/.*\.html)$ !
ProxyErrorOverride On
ProxyPass        /      http://192.168.56.2:8081/
ProxyPassReverse /      http://192.168.56.2:8081/
```



없는 페이지 NoExistPage 를 다시 호출한다면

```sh
$ curl -v $(hostname -i):80/NoExistPage
* About to connect() to 192.168.56.2 port 80 (#0)
*   Trying 192.168.56.2...
* Connected to 192.168.56.2 (192.168.56.2) port 80 (#0)
> GET /NoExistPage HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 192.168.56.2
> Accept: */*
>
< HTTP/1.1 404 Not Found
< Date: Tue, 11 Oct 2022 01:42:41 GMT
< Server: Apache
< Last-Modified: Tue, 11 Oct 2022 01:22:38 GMT
< ETag: "19-5eab81c966288"
< Accept-Ranges: bytes
< Content-Length: 25
< Content-Type: text/html
<
apache_2.4.54/error.html
```

HTTP Status Code 404 Not Found (_아까와 조금 다르지만_) 가 전달되고, Apache의 Error page가 보여진다.



## 4.3 WAS Down 상황에서의 Error Handling

`ProxyErrorOverride Off` 설정을 하면 Tomcat의 Error는 Tomcat에서 처리된다.

Tomcat이 Shutdown 상태에서는,

```sh
$ curl -v $(hostname -i):80/NoExistPage
* About to connect() to 192.168.56.2 port 80 (#0)
*   Trying 192.168.56.2...
* Connected to 192.168.56.2 (192.168.56.2) port 80 (#0)
> GET /NoExistPage HTTP/1.1
> User-Agent: curl/7.29.0
> Host: 192.168.56.2
> Accept: */*
>
< HTTP/1.1 503 Service Unavailable
< Date: Tue, 11 Oct 2022 01:56:33 GMT
< Server: Apache
< Last-Modified: Tue, 11 Oct 2022 01:22:38 GMT
< ETag: "19-5eab81c966288"
< Accept-Ranges: bytes
< Content-Length: 25
< Connection: close
< Content-Type: text/html
<
apache_2.4.54/error.html
```



mod_proxy 모듈이 Tomcat 연결이 되지 않아 자체적으로 HTTP 503 Service Unavailable 를 생산하며,

Apache의 Error page를 호출하였다.



## 4.4 LB 환경에서의 Error Handling

WEB &rarr; LB &rarr; WAS 환경에서, WAS Down 시에 LB는 HTTP 502 또는 503 를 Return 할 수 있겠다.



LB는 해당 이슈 재현시에 Apache 를 사용했지만, 다음과 같이 최대한 LB와 유사하게 하기 위해 설정하였다.

 ```LB
 <IfDefine Multi-Line-Comments>
   ErrorDocument 404 /error.html
   ErrorDocument 500 /error.html
   ErrorDocument 502 /error.html
   ErrorDocument 503 /error.html
 </IfDefine>
 
 ProxyPassMatch ^(/.*\.html)$ !
 ProxyErrorOverride Off
 ProxyPass        /      http://192.168.56.2:8081/
 ProxyPassReverse /      http://192.168.56.2:8081/
 ```

> IfDefine 허수 변수값을 선언하여 범위 주석을 하였다.



최전선 WEB은 다음 설정을 하였다.

```httpd.conf
ErrorDocument 404 /error.html
ErrorDocument 500 /error.html
ErrorDocument 502 /error.html
ErrorDocument 503 /error.html

ProxyPassMatch ^(/.*\.html)$ !
ProxyErrorOverride On 502 503
ProxyPass        /      http://192.168.56.2:180/
ProxyPassReverse /      http://192.168.56.2:180/
```

HTTP Status Code `502, 503` 에 대해서만 Apache WEB에서 ErrorDocument 처리한다.



여기 내용에서는 `ProxyErrorOverride` 의 3번째 Arguments를 통해 특정 HTTP Status Code를 직접 Handling 할 수 있다는 것을 살펴보기 위함이다.

굳이 LB 를 예시로 든것이다.

특별한 사정이 있는 것은 아니다
