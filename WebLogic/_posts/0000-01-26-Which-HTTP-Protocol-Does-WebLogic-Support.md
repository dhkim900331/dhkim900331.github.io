---
date: 2026-02-23 13:44:32 +0900
layout: post
title: "[WebLogic/HTTP] Which HTTP Version Does WebLogic 14c Support?"
tags: [Middleware, WebLogic, HTTP]
typora-root-url: ../..
---

# 1. Overview

WebLogic 14c 에서 제공하는 HTTP Version은 무엇인가요?

<br><br>


# 2. Descriptions

[Overview of Configuring Web Server Components](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/cnfgd/web_server.html#GUID-EE744F0C-BC36-42A2-96A8-7A0F2C6C2680) 설명에 따르면, HTTP 1.1 표준을 지원합니다.

[WebLogic 14.1.1 부터 Java EE 8 / Servlet 4.0 을 지원](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/notes/whatsnew.html#GUID-E5A5ADC4-7715-4DD9-A1BF-E2A4A5BE4BE3)하여, HTTP 2 또한 지원합니다.

즉, WebLogic 14.1.1 은 HTTP/1.1, HTTP/2 를 지원합니다. [Other Standards](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/notes/whatsnew.html#GUID-5BDC60E2-9FC7-4BEC-A3CA-5EBF109F6EB9)

<br>

curl 유틸리티와 같은 프로그램으로 WebLogic Server에 직접적으로 호출 시 HTTP/1.1 으로 응답합니다.

```sh
$ curl -v http://<WLS_IP>:<WLS_PORT>/path-to-sample-app/index.jsp
*   Trying X.X.X.X...
* TCP_NODELAY set
* Connected to <WLS_IP> (X.X.X.X) port <WLS_PORT> (#0)
> GET /path-to-sample-app/index.jsp HTTP/1.1
> Host: <WLS_IP>:<WLS_PORT>
> User-Agent: curl/7.61.1
> Accept: */*
>
< HTTP/1.1 200 OK
...
```

<br>

WebLogic 14.1.1 부터 지원되는 HTTP/2 는 기본적으로 활성화 되어 있습니다.

`--http2` argument를 이용해 호출 시, HTTP/2 로 전환됩니다.

```sh
$ curl -v --http2 http://<WLS_IP>:<WLS_PORT>/path-to-sample-app/index.jsp
*   Trying X.X.X.X...
* TCP_NODELAY set
* Connected to <WLS_IP> (X.X.X.X) port <WLS_PORT> (#0)
> GET /path-to-sample-app/index.jsp HTTP/1.1
> Host: <WLS_IP>:<WLS_PORT>
> User-Agent: curl/7.61.1
> Accept: */*
> Connection: Upgrade, HTTP2-Settings
> Upgrade: h2c
> HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA
>
< HTTP/1.1 101 Switching Protocols
< Connection: Upgrade
< Date: Wed, 28 Jan 2026 01:15:13 GMT
< Content-Length: 0
< X-ORACLE-DMS-RID: 0
< Upgrade: h2c
< X-ORACLE-DMS-ECID: 81dc7a0e-2cb3-41b7-b3aa-5cbb5ede66c8-0000001e
* Received 101
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* Connection state changed (MAX_CONCURRENT_STREAMS == 300)!
< HTTP/2 200
...
```


<br><br>


SSL이 활성화된 WebLogic Server에 연결 시, 기본적으로 HTTP/2 로 협상 됩니다.

```sh
$ curl -v -k https://<WLS_IP>:7002/path-to-sample-app/index.jsp
*   Trying X.X.X.X...
* TCP_NODELAY set
* Connected to <WLS_IP> (X.X.X.X) port 7002 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /etc/pki/tls/certs/ca-bundle.crt
  CApath: none
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
...
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server accepted to use h2
...
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* TLSv1.3 (OUT), TLS app data, [no content] (0):
* TLSv1.3 (OUT), TLS app data, [no content] (0):
* TLSv1.3 (OUT), TLS app data, [no content] (0):
* Using Stream ID: 1 (easy handle 0x55b3a8d056f0)
* TLSv1.3 (OUT), TLS app data, [no content] (0):
> GET /path-to-sample-app/index.jsp HTTP/2
> Host: <WLS_IP>:7002
> User-Agent: curl/7.61.1
> Accept: */*
>
...
< HTTP/2 200
```


<br><br>


Chrome 등 브라우저를 통하여 HTTP 사이트에 연결하면, HTTP/1.1 으로만 협상이 됩니다.

HTTP/2 사양 자체는 Encryption 환경, 즉 SSL 사용이 필수로 요구되지 않습니다만,

여러 Browser에서는 h2c(HTTP/2 cleartext) 를 허용하지 않도록 구현하기 위해 HTTPS 사이트 연결시에만, HTTP/2 를 협상합니다.

즉, HTTP/2 표준과 이를 구현한 브라우저 에서는 다르게 동작한다는 것입니다.

[Does HTTP/2 require encryption?](https://http2.github.io/faq/#does-http2-require-encryption)


<br><br>


다음 옵션을 적용하여, HTTP/2 협상을 제어 할 수 있습니다.

앞으로 모든 통신은 HTTP/1.1 로 유지됩니다.

`-Dweblogic.http.disablehttp2=true`

<br>

`--http2` 등과 같이 명시적으로 HTTP/2 협상을 요청하면, 다음처럼 `505 HTTP Version Not Supported` 거부 됩니다.

```sh
$ curl -v --http2 http://<WLS_IP>:<WLS_PORT>/path-to-sample-app/index.jsp
*   Trying X.X.X.X...
* TCP_NODELAY set
* Connected to <WLS_IP> (X.X.X.X) port <WLS_PORT> (#0)
> GET /path-to-sample-app/index.jsp HTTP/1.1
> Host: <WLS_IP>:<WLS_PORT>
> User-Agent: curl/7.61.1
> Accept: */*
> Connection: Upgrade, HTTP2-Settings
> Upgrade: h2c
> HTTP2-Settings: AAMAAABkAAQCAAAAAAIAAAAA
>
< HTTP/1.1 101 Switching Protocols
< Connection: Upgrade
< Date: Wed, 28 Jan 2026 01:17:31 GMT
< Content-Length: 0
< X-ORACLE-DMS-RID: 0
< Upgrade: h2c
< X-ORACLE-DMS-ECID: fbfe3cfc-7e18-405a-84c1-86287a9da20b-0000000e
* Received 101
* Using HTTP2, server supports multi-use
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* Connection state changed (MAX_CONCURRENT_STREAMS == 300)!
< HTTP/2 505
```

<br>

정리하면,

WebLogic 14.1.1 부터 Java EE 8.0 / Servlet 4.0 지원됨에 따라, 기본/표준 HTTP/1.1 에 HTTP/2 를 사용할 수 있습니다.

또한, SSL 환경에서는 기본적으로 HTTP/2 로 협상이 되며,

특정 옵션을 적용하여 HTTP/2 협상을 명시적으로 제어 할 수 있습니다.

<br>

HTTP/2 자체에 대해 더 많은 궁금한 사항은 [HTTP/2 Home page](https://http2.github.io/)를 참고하시기 바랍니다.


<br><br>


# 3. References

KB867747 Which HTTP Version Does WebLogic 14c Support?
