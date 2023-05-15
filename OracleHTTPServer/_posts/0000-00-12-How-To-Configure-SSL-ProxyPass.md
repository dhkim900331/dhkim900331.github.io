---
date: 2023-05-16 07:39:11 +0900
layout: post
title: "[OracleHTTPServer/SSL] How to Configure SSL ProxyPass"
tags: [OracleHTTPServer, OHS, Apache, SSL, ProxyPass, HTTPS]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 12cR2 에서 ProxyPass SSL 구현 방법



# 2. Server SSL 설정

Server가 되는 SSL Site에 Wallet 인증서를 구현한다.



Wallet 생성

```sh
$ orapki wallet create -wallet <Wallet dir> -pwd <Wallet pwd> -auto_login
$ orapki wallet add -wallet ${CERT} -pwd <Wallet pwd> \
  -dn "CN=`hostname`, OU=Example Department, O=Example Company, L=Birmingham, ST=West Midlands, C=GB" \
  -keysize 1024 -self_signed -validity 3650
```



SSL.conf 구현

```
SSLEngine on
SSLVerifyClient None
SSLProtocol TLSv1.2
SSLHonorCipherOrder on
SSLCipherSuite HIGH:MEDIUM:!aNULL:!MD5:!RC4:!eNULL
SSLCRLCheck Off
SSLWallet "/sw/webtier/12cR2/domains/base_domain/worker2-cert"
```



# 3. Client SSL 설정

ProxyPass로 Server 에 SSL로 접근하는 Wallet 설정을 구현한다.



Server SSL을 Chrome Browser 또는 openssl 명령으로 다운로드 받는다.

openssl 예시로는

```sh
$ openssl s_client <Server SSL Site>
...
-----BEGIN CERTIFICATE-----
<certificate contents>
...
-----END CERTIFICATE-----
```



BEGIN~END 전체를 복사하여 별도로 저장한다.



Wallet 을 생성하여 Server 측 인증서를 삽입한다.

```sh
$ orapki wallet add -wallet <Wallet dir> -pwd <Wallet pwd> \
-trusted_cert -cert <Server SSL Site's SSL File>
```



HTTPD.conf 구현

```
SSLProxyEngine on
SSLProxyVerify None
SSLProxyWallet "<Wallet Dir>"

<LocationMatch /ssl>
  ProxyPass https://<Servet Site's SSL Addr>/
  ProxyPassReverse https://<Servet Site's SSL Addr>/
</LocationMatch>
```



Client OHS Component의 `/ssl` 요청 시 Server OHS Component의 SSL Page를 호출한다.



# 4. References

https://oracle-base.com/articles/12c/oracle-http-server-ohs-configure-ssl

