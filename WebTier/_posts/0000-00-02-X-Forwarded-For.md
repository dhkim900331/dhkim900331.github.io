---
date: 2022-05-09 15:45:29 +0900
layout: post
title: "[WebTier/Apache] X-Forwarded-For"
tags: [WebTier, OHS, Apache, XFF, RewriteRule]
typora-root-url: ..
---

# 1. 개요

얼마 전 고객사에서 XFF Header 값이 Apache Access Log에 찍히지 않았다.

앞단 Load Balancer에도 정상적으로 설정이 완료되었다는 엔지니어 확인 결과에도 동작하지 않았다.

사무실로 돌아와 LB 환경을 만들 수 없어, Apache VM을 2대를 이용하여 LB -> WEB 환경을 모방하며 테스트 해보았다.



# 2. Request Flow

![X-Forwarded-For_1](/../assets/posts/images/WEB/X-Forwarded-For/X-Forwarded-For_1.png)



* Request가 들어올 경우, 어떠한 흐름으로 처리되는지를 이해하기 위한 그림이다.
* 순서대로, 사용자(Client) / LB (wellknown.com) / WEB (innerweb.com)
* 사용자가 `http://wellknown.com` 접속 하면, LB는 곧이 곧대로 `http://innerweb.com` 에 proxy pass 한다.
* WEB (innerweb.com) 은 `http to https` 전환을 위해 RewriteRule 을 사용했다.



## 2.1 LB (wellknown.com)

* LB의 역할을 유사하게 하기 위해, HTTP와 HTTPS를 연결해주는 2개의 VirtualHost가 있다.

```bash
# 1. HTTP
Listen 80

<VirtualHost *:80>
ServerName wellknown.com

RewriteEngine On
RewriteCond %{HTTP_HOST} ^wellknown.com [NC]
RewriteCond %{SERVER_PORT} 80
RewriteRule ^/(.*)$ http://innerweb.com/$1 [P,L]
</VirtualHost>
```

> HTTP 접속 시 , HTTP WEB으로 Proxied



```bash
# 2. HTTPS
Listen 443

SSLPassPhraseDialog  builtin
SSLCertificateFile    ${SRVROOT}/cert/wellknown.com.crt
SSLCertificateKeyFile ${SRVROOT}/cert/private.key

<VirtualHost *:443>
ServerName wellknown.com

SSLEngine On
SSLProxyEngine On
SSLProxyVerify none
SSLProxyCheckPeerCN off
SSLProxyCheckPeerName off
SSLProxyCheckPeerExpire off

RewriteEngine On
RewriteCond %{HTTP_HOST} ^wellknown.com [NC]
RewriteCond %{SERVER_PORT} 443
RewriteRule ^/(.*)$ https://innerweb.com/$1 [P,L]
</VirtualHost>
```

> HTTPS 접속 시, HTTPS WEB으로 Proxied
>
> LB 자체에도 https 통신을 위해 인증서가 필요하니, `wellknown.com.crt` 사설 인증서를 적용했다.



## 2.2 WEB (innerweb.com)

* endpoint 인 WEB에는 `http to https` 역할만 추가로 있다.

```bash
ServerName innerweb.com
RewriteEngine On

# 1. HTTP to HTTPS
RewriteCond %{HTTP_HOST} ^innerweb\.com
RewriteCond %{SERVER_PORT} 80
RewriteRule ^/(.*)$ https://wellknown.com/$1 [R,L]
```



* 그리고, HTTPS VirtualHost가 있다.

```bash
SSLPassPhraseDialog  builtin
SSLCertificateFile          ${CERT}/innerweb.com.crt
SSLCertificateKeyFile       ${CERT}/private.key

<VirtualHost *:443>
ServerName innerweb.com
SSLEngine on
</VirtualHost>
```



# 3. XFF 호출 테스트

* LogFormat은 다음과 같다.

```bash
LogFormat "XFF=%{X-Forwarded-For}i A=%a H=%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %D" combined
```



* Client IP가 `192.168.5.61` 인 곳에서, `http://wellknown.com` 호출 시. WEB http Access Log

```bash
XFF=192.168.56.1 A=192.168.56.2 H=192.168.56.2 - - [09/May/2022:15:03:00 +0900] "GET / HTTP/1.1" 302 206 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36" 237
```



* 위 요청 시, 자동으로 사용자는 HTTP 302 `https://wellknown.com` 을 접속한다. 이때 WEB https Access Log

```bash
XFF=192.168.56.1 A=192.168.56.2 H=192.168.56.2 - - [09/May/2022:15:04:56 +0900] "GET / HTTP/1.1" 200 613 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36" 538
```



# 4. 마무리

사실상 표준 헤더(사실 표준 아님)인 XFF Header는 가공할 이유가 없다.

앞단 LB에서 XFF = Client.IP 를 가공해서 넘겨주기만 하면 되기 때문이다.

그러나, 어느 고객사 작업 시 HTTP 채널에서는 문제가 없으나, HTTPS 채널에서는 XFF 값이 보이지 않는 이슈가 있었는데

이를 증명 하기 위해 테스트하고 기록하였다.



다시금 고객하고 컨택하며, LB측 확인을 요청해야 겠지만..

그때 다시 결과를 기록하도록 한다.
