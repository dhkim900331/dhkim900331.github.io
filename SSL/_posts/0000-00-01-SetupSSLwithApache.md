---
date: 2022-04-27 13:13:10 +0900
layout: post
title: "[SSL/Apache] 사설 SSL 인증서 사용과 검증"
tags: [SSL, Apache, Openssl, Tomcat]
typora-root-url: ..
---

# 1. Overview

안녕하세요.

오늘은, WEB/WAS 에서 자주 언급되고 사용되는 SSL 인증서의 기본 학습을 위한 테스트를 진행해볼까 합니다.

최근에 고객사에서 사용하던 SSL 인증서가 만료시점이 되어, 파일 교체를 하였다고 합니다.

교체한 인증서와 기존에 사용하고 있던 인증서 내용이 다르지 않고, Expire (만료기간)만 갱신된 동일한 인증서라면 

별다른 트러블이 발생하지 않겠지만, 어떠한 문제가 발생을 하였는지 SSL 인증 거부로 통신이 되지 않는 이슈가 있었습니다.

이러한 상황에 맞닥뜨렸을 때, 기본적으로 어떠한 방법을 통해 SSL 인증서에 문제가 없는지 테스트를 진행해보겠습니다.

<br>

* 이슈가 발생한 고객사의 환경은, 우리가 많이 어디선가 접한, 일반적인 REST API 호출 부분에서의 SSL 인증 문제 였습니다.
  * WAS AP(Tomcat) 에서 REST API 를 이용하여 Remote AP(Apache)를 호출합니다.
  * WAS AP(Tomcat) / Remote AP(Apache) 양쪽간의 SSL 인증서가 동일하게 교체 되었지만 API 호출 시 SSL 인증 거부 이슈 발생 했습니다.

<br>

* 다음의 Step 을 진행하며, SSL 인증서가 유효하게 적용되고 동작하고 있는지 검증하는 것을 알 수 있습니다.
  * 사설/비-사설 SSL인증서의 검증 방법 등을 확인
  * 사설(Self-Signed) SSL 인증서를 Remote AP(Apache)에 Setup
  * HTTPS 통신을 하며, SSL 인증서 검증
  * WAS AP(Tomcat)에 SSL 클라이언트 인증서를 Setup. HTTPS 연결을 수행.


<br><br>


# 2. SSL 인증서 생성

* 인증서의 생성이 되고, 위치할 `CERT` 디렉토리를 만들어줍니다.

```bash
$ mkdir /tmp/self_signed_cert
$ CERT=/tmp/self_signed_cert
```

<br>


## 2.1 Private Key

```bash
$ openssl genrsa -des3 -out ${CERT}/private.key
Generating RSA private key, 2048 bit long modulus (2 primes)
.......+++++
..............................................................+++++
e is 65537 (0x010001)
Enter pass phrase for /tmp/self_signed_cert/private.key: (dhkim)
Verifying - Enter pass phrase for /tmp/self_signed_cert/private.key: (dhkim)
```

> 개인키의 패스워드로 `dhkim` 을 사용했습니다.
>
> 패스워드를 사용하지 않으려면 `-des3` 옵션을 제거 합니다.

<br>


## 2.2 CSR

* 제가 직접 생성한 (혹은 고객) 인증서는 최상위 기관(root) 에 제출해야 합니다.

  최상위 기관(root Certificate Authority; root CA)에서 서명(제출한 인증서를 유효하다고 인증과 같은 절차)을 받기 위해 필요합니다.

```bash
$ openssl req -new -key ${CERT}/private.key -out ${CERT}/root.csr \
-subj "/C=KR/ST=Seoul/L=Seocho-gu/O=OSCI/OU=Cloud Migration/CN=dhkim.com"
```

<br>


## 2.3 Self-Signed

* 우리가 사용하는 Chrome 과 같은 Browser에는 아래에서 언급하는 *신뢰할 수 있는 상위 기관*들의 인증서가 이미 포함되어 있습니다.

  자체 서명한 인증서를 사용하면, Browser에 설치되어 있는 인증서로 유효한지 확인을 합니다.

<br>

* 위에서 만든 개인키(`private.key`)와 제출하는 인증 요청서(`root.csr`)을 가지고, 직접 서명할 수 있습니다.

  내 자신이 최상위 기관이 되어, 스스로를 서명하는 것입니다.

  이것을 말 그대로 Self-Signed 라고 하며, 해당 인증서를 사용하여 HTTPS 연결을 시도하면

  상위 기관(rootCA or intermediate ca) 에서 인증되지 않아 경고가 나타납니다.

```bash
$ openssl x509 -req -days 365 \
-in ${CERT}/root.csr \
-signkey ${CERT}/private.key \
-out ${CERT}/dhkim.com.crt
---stdout below---
Signature ok
subject=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
Getting Private key
Enter pass phrase for /tmp/self_signed_cert/private.key: (dhkim)
```

<br>


# 3. 인증서 적용

```bash
Listen 443
Define CERT "/tmp/self_signed_cert"
SSLPassPhraseDialog  exec:${SRVROOT}/bin/sslpass.sh
SSLCertificateFile          ${CERT}/dhkim.com.crt
SSLCertificateKeyFile       ${CERT}/private.key

<VirtualHost *:443>
    SSLEngine on
    ServerName dhkim.com

    DocumentRoot "/tmp/htdocs_ssl"
    <Directory "/tmp/htdocs_ssl">
        Options None
        AllowOverride None
        Require all granted
    </Directory>
</VirtualHost>
```

> PC의 hosts 파일에 `dhkim.com` 을 등록하고, 접속할 수 있습니다.


* 접속 시 아래와 같이 완료되었습니다.

![SetupSSLwithApache_1](/../assets/posts/images/SSL/SetupSSLwithApache/SetupSSLwithApache_1.png)


<br><br>


# 4. HTTS 테스트

## 4.1 curl

### (1). 기본 인증서 사용

```bash
$ curl -v https://dhkim.com
* Rebuilt URL to: https://dhkim.com/
*   Trying 192.168.56.2...
* TCP_NODELAY set
* Connected to dhkim.com (192.168.56.2) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /etc/pki/tls/certs/ca-bundle.crt
  CApath: none
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS handshake, Certificate (11):
* TLSv1.2 (OUT), TLS alert, unknown CA (560):
* SSL certificate problem: self signed certificate
* Closing connection 0
curl: (60) SSL certificate problem: self signed certificate
More details here: https://curl.haxx.se/docs/sslcerts.html

curl failed to verify the legitimacy of the server and therefore could not
establish a secure connection to it. To learn more about this situation and
how to fix it, please visit the web page mentioned above.
```

> `CAfile: /etc/pki/tls/certs/ca-bundle.crt` 인증서 파일을 사용하여 `dhkim.com` 인증을 하려고 합니다.
>
> 앞서 우리가 만든 SSL 인증서는, 어떠한 공증된 상위 기관에서 인증해준 것이 아니라
>
> 자체 서명(Self-Signed) 하였기 때문에 CA를 알 수 없습니다. 아래가 그 로그입니다.
>
> `TLSv1.2 (OUT), TLS alert, unknown CA (560):` 
>
> `SSL certificate problem: self signed certificate` 
>
> SSL 인증 문제의 원인으로 자체 서명된 인증서로 로그가 출력되었습니다.
>
> 정확히는 curl 이 사설 인증서 인지를 알고 있는 것이 아니라, 
>
> 어디에도 서명(Signed) 되어 있지 않음을 원인으로 알려준 것입니다.

<br>


### (2). 사설 인증서 사용

* 사설 인증서를 가지고 `curl`을 수행하니, 정상적으로 SSL Handshake가 이루어지고 연결이 되는 것을 확인해봅니다.

  우리가 원격지의 Server와 SSL 통신을 수행해야 할 때, 가지고 있는 인증서가 유효한지 `curl` 의 간단한 명령으로도 확인이 가능하다는 것을 알 수 있습니다.

```bash
$ curl -v https://dhkim.com --cacert ${CERT}/dhkim.com.crt
* Rebuilt URL to: https://dhkim.com/
*   Trying 192.168.56.2...
* TCP_NODELAY set
* Connected to dhkim.com (192.168.56.2) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /tmp/self_signed_cert/dhkim.com.crt
  CApath: none
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, [no content] (0):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server accepted to use http/1.1
* Server certificate:
*  subject: C=KR; ST=Seoul; L=Seocho-gu; O=OSCI; OU=Cloud Migration; CN=dhkim.com
*  start date: May 10 09:48:47 2022 GMT
*  expire date: May 10 09:48:47 2023 GMT
*  common name: dhkim.com (matched)
*  issuer: C=KR; ST=Seoul; L=Seocho-gu; O=OSCI; OU=Cloud Migration; CN=dhkim.com
*  SSL certificate verify ok.
* TLSv1.3 (OUT), TLS app data, [no content] (0):
> GET / HTTP/1.1
> Host: dhkim.com
> User-Agent: curl/7.61.1
> Accept: */*
>
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS app data, [no content] (0):
< HTTP/1.1 200 OK
< Date: Wed, 11 May 2022 04:08:14 GMT
< Server: Apache
< Last-Modified: Wed, 11 May 2022 03:47:47 GMT
< ETag: "c-5deb44dfe095d"
< Accept-Ranges: bytes
< Content-Length: 12
< Content-Type: text/html
<
hello world
* Connection #0 to host dhkim.com left intact
```

> `CAfile: /tmp/self_signed_cert/dhkim.com.crt` 인증서를 지정할 수 있습니다.
>
> `11~23 Line` SSL handshake 가 정상적으로 문제없이 일어났습니다.
>
> `24 Line` TLSv1.4 버전 프로토콜 / 암호화 알고리즘 로그가 확인됩니다.
>
> `26~32 Line` subject(보안 대상; 웹서버)와 issuer(발급자; 인증서 증명자)의 정보입니다.

<br>


### (3). 사설 인증서 사용 (download ssl)

* 원격지의 SSL 인증서를 역으로 다운로드 받아, 활용하는 방법도 해볼 수 있습니다. 

  굳이 접속을 하기 위해 SSL 인증서를 손에 쥐고 있을 필요가 없습니다.

```bash
$ openssl s_client -servername dhkim.com -connect 192.168.56.2:443 -showcerts > ${CERT}/download_dhkim.com.crt

$ ls -rtl ${CERT}/download_dhkim.com.crt
-rw-rw-r--. 1 dhkim dhkim 6220  5월 11 13:15 /tmp/self_signed_cert/download_dhkim.com.crt
```

> `openssl` 명령으로, 원격지의 SSL 인증서를 다운로드 받았습니다.


* 기존에 우리가 가지고 있던 원본 SSL 인증서와, 방금 다운로드 받은 SSL 인증서는 무슨 차이가 있길래, 

  용량도 내용의 길이면도 차이가 있을까요?

```bash
$ ls -rtl ${CERT}/*crt
-rw-rw-r--. 1 dhkim dhkim 1237  5월 10 18:48 /tmp/self_signed_cert/dhkim.com.crt
-rw-rw-r--. 1 dhkim dhkim 6220  5월 11 13:15 /tmp/self_signed_cert/download_dhkim.com.crt
```


* 용량도, 내용도 달라보이지만 사실상 차이는 없습니다. 

  내용을 비교하면 `download_dhkim.com.crt` 파일이 좀 더 방대하지만, 
  `BEGIN CERTIFICATE` 으로 시작하여 `END CERTIFICATE` 으로 끝나는 사이의 암호화된 인증서 정보는 같습니다.
  
  다른 내용은 필요 없고, 암호화된 인증서 정보만을 가지고 SSL 인증을 수행하기 때문입니다.

<br>

* 다운로드 받은 인증서로 연결을 수행해봅시다.

```bash
$ curl -v https://dhkim.com --cacert ${CERT}/download_dhkim.com.crt
* Rebuilt URL to: https://dhkim.com/
*   Trying 192.168.56.2...
* TCP_NODELAY set
* Connected to dhkim.com (192.168.56.2) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
* successfully set certificate verify locations:
*   CAfile: /tmp/self_signed_cert/download_dhkim.com.crt
  CApath: none
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.3 (OUT), TLS handshake, [no content] (0):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server accepted to use http/1.1
* Server certificate:
*  subject: C=KR; ST=Seoul; L=Seocho-gu; O=OSCI; OU=Cloud Migration; CN=dhkim.com
*  start date: May 10 09:48:47 2022 GMT
*  expire date: May 10 09:48:47 2023 GMT
*  common name: dhkim.com (matched)
*  issuer: C=KR; ST=Seoul; L=Seocho-gu; O=OSCI; OU=Cloud Migration; CN=dhkim.com
*  SSL certificate verify ok.
* TLSv1.3 (OUT), TLS app data, [no content] (0):
> GET / HTTP/1.1
> Host: dhkim.com
> User-Agent: curl/7.61.1
> Accept: */*
>
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, [no content] (0):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS app data, [no content] (0):
< HTTP/1.1 200 OK
< Date: Wed, 11 May 2022 04:16:06 GMT
< Server: Apache
< Last-Modified: Wed, 11 May 2022 03:47:47 GMT
< ETag: "c-5deb44dfe095d"
< Accept-Ranges: bytes
< Content-Length: 12
< Content-Type: text/html
<
hello world
* Connection #0 to host dhkim.com left intact
```

> 전혀 문제 없이, SSL Handshake 수행됩니다.

<br>


## 4.2 openssl

### (1). 기본 인증서 사용

```bash
$ openssl s_client -servername dhkim.com -connect 192.168.56.2:443
CONNECTED(00000003)
depth=0 C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
verify error:num=18:self signed certificate
verify return:1
depth=0 C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
verify return:1
---
Certificate chain
 0 s:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
   i:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDYzCCAksCFDfIh7j8xqsFYz9suq3XIC9rAG6PMA0GCSqGSIb3DQEBCwUAMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTAeFw0yMjA1MTAwOTQ4NDdaFw0yMzA1MTAwOTQ4NDdaMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALYY
RPC8/lh6TPsWmhqgtpb5GUAfODUahfkkklR0pUafCPpVyfAoBKzMcYgEU8kK0ETf
T8jF9LrforRAa6rrm7e2I3N93TzUgypRAdJeoFC1Eg1YpchHGHkoDVrMqMZdCjVZ
+2QR0E8B16RedzCY55ctb0dCHckoD4nnzwvm6HInpFK6DrZBxdbEh1Dr8hiEsWtH
bYeHGFWc/ugmAlVzuQLNevInKS9pUFglb7yxYpkVI4wf6C/Hyf0Wba34yBcGLtbr
cF32TJrp12wAq1D16jUX1fDwiiq6P9mo0Xxw2bza17PyzeV++i2DszRjhgh9A1RE
6A/ZX15gtgYY4Bsp4e8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAgwp7vJb24g6r
78VPi3UwEkgSRbSnc9yK2KlObc2xtwK5TbibeIPdbkw5vPj9tieCgNyvKfpWnIni
/CvDILdaRnAMcCbP2O3cNBK/xQDvL1pw3GMzWaZvPgqGNNQ1GOD5FzPnBXniOG8T
OsY54KG31zLp7/JslJ7CmtfFFXRRMMYIRXBMJdNNZE4n4j6+SNOdhFlxAqGevrzE
qKAndFkRsr//le62ddeegVZdiZiEZfbPNx3ebfs98VXV7HyvsDt3H/oRGXsBF1gl
DyqobfbdovazynOi/NHZN2JJEaZREVM7itozp26cIfmgEXwWkGEocPZOGMAQYDo2
5fq8KSWaKg==
-----END CERTIFICATE-----
subject=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

issuer=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 1431 bytes and written 387 bytes
Verification error: self signed certificate
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 2048 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 18 (self signed certificate)
---
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: 9EF9BB21AB914D0155A71BC146167828D773705EFF8B04608CC9C7EAD688C656
    Session-ID-ctx:
    Resumption PSK: 96F5690C7A6D733E7CB1A0F5DD595908F8A50F1D7209D831FBF5F198228DB4689EE7097958AAA599527BA18883A45E46
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 300 (seconds)
    TLS session ticket:
    0000 - 1f be 43 bb 42 73 6a cf-2a cb cc 05 fc 02 6d aa   ..C.Bsj.*.....m.
    0010 - c7 68 0c b6 bc 20 ae e4-96 38 a0 82 3c 36 a3 96   .h... ...8..<6..
    0020 - 7a 2f 7b 92 b2 ce 7c 68-ad b1 3a b3 6d 6f 7e 09   z/{...|h..:.mo~.
    0030 - 56 61 c5 65 e4 91 0c e3-b0 47 58 c4 e8 95 f7 6b   Va.e.....GX....k
    0040 - 0a f2 4e e1 b4 bf 9b 71-6d 10 c7 21 99 6d 94 62   ..N....qm..!.m.b
    0050 - 02 b9 b7 34 5e 5c dd 55-69 95 de 3c 5f bd 81 e2   ...4^\.Ui..<_...
    0060 - f9 06 29 bf f4 85 0c 96-e3 87 d5 0a 08 14 9d b2   ..).............
    0070 - 72 2c 22 40 b2 4e ad 12-55 82 4a 70 35 cf 76 cb   r,"@.N..U.Jp5.v.
    0080 - d8 ac 34 d3 c5 ce fe 04-9b d3 31 66 0b 55 3b b3   ..4.......1f.U;.
    0090 - 40 e1 33 45 2e ac 95 da-9d 60 a1 78 f5 62 f4 3a   @.3E.....`.x.b.:
    00a0 - 8d 67 2f 3a de 55 cc 40-08 81 df 2f 2c 57 4f 89   .g/:.U.@.../,WO.
    00b0 - 6b 7b 45 8b 0a df e4 11-c6 db f0 b2 9f 82 76 4c   k{E...........vL
    00c0 - c0 53 7f 6a 23 7d 23 b3-73 c4 41 4d f6 98 5a 43   .S.j#}#.s.AM..ZC
    00d0 - 31 dd 58 31 d2 0b ab 81-90 5c 67 44 70 ec 19 a0   1.X1.....\gDp...
    00e0 - 99 cc 07 99 5b e1 7d 11-a1 5f bf f5 4f e8 b3 2a   ....[.}.._..O..*

    Start Time: 1652242972
    Timeout   : 7200 (sec)
    Verify return code: 18 (self signed certificate)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: 9FFF3FB5D62CB380CC9836ED892D93A84B4D11B64B25A100DBFA5E44612B20F2
    Session-ID-ctx:
    Resumption PSK: AE2689A89A2E0F14B5041F9CDA86E749663469A000ACD4D834BA40772D3A25B9D887F6C12672B251A906F4CC0D7D67AC
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 300 (seconds)
    TLS session ticket:
    0000 - 1f be 43 bb 42 73 6a cf-2a cb cc 05 fc 02 6d aa   ..C.Bsj.*.....m.
    0010 - 3f fb af c5 b8 3e 39 1f-b7 a5 48 85 e4 cc ae 36   ?....>9...H....6
    0020 - 66 22 f8 fc 25 e7 38 c7-2f 1d 8b 0a ba 8c 92 cd   f"..%.8./.......
    0030 - af 02 55 3d 02 29 ea 1a-cb a4 7e bc b4 21 74 82   ..U=.)....~..!t.
    0040 - 6a 41 45 67 a9 1c 4f eb-a2 02 81 bd 65 cf da 59   jAEg..O.....e..Y
    0050 - 25 bc 99 3e 0e aa 1e 6c-de 7a 77 0a 5d 98 96 96   %..>...l.zw.]...
    0060 - 39 85 18 df dc 8d 53 52-73 c6 0b 40 f1 4f 23 fa   9.....SRs..@.O#.
    0070 - ab df 68 da 09 84 2f 1e-47 13 3f ba 4b c6 c1 a4   ..h.../.G.?.K...
    0080 - dd 23 bb ce 83 35 98 a1-3e 3d 6e dc 2e cb 71 fe   .#...5..>=n...q.
    0090 - 98 51 63 ce aa 61 98 38-ee 82 84 8a a3 97 28 a1   .Qc..a.8......(.
    00a0 - 22 88 08 53 cb 3d 59 78-09 c6 ea 8a 71 c0 ee cc   "..S.=Yx....q...
    00b0 - a0 6c 71 bc 0b 26 5a 52-65 3e 77 9e b3 3c b6 80   .lq..&ZRe>w..<..
    00c0 - d4 fb 98 9b c2 e9 a4 e0-14 49 c1 ae 42 8d a2 5f   .........I..B.._
    00d0 - 6b 0d b7 94 f3 42 50 5d-6f 98 33 e8 1f 8a e7 2e   k....BP]o.3.....
    00e0 - 75 cc a8 52 64 cd d7 bd-c2 59 c9 b5 a5 ac ea e1   u..Rd....Y......

    Start Time: 1652242972
    Timeout   : 7200 (sec)
    Verify return code: 18 (self signed certificate)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK

HTTP/1.1 400 Bad Request
Date: Wed, 11 May 2022 04:22:52 GMT
Server: Apache
Content-Length: 226
Connection: close
Content-Type: text/html; charset=iso-8859-1

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
</p>
</body></html>
closed
```

> `openssl` 을 이용하면, 기본적으로 SSL 연결은 정상적으로 수행되지만,
>
> `Verification error: self signed certificate` 와 같이 경고성 메시지를 출력해주고 있습니다.

<br>


### (2). 사설 인증서 사용

* 위에서 해본 것처럼, SSL 인증서를 지정하여 확인해볼 수 있습니다.

```bash
$ openssl s_client -servername dhkim.com -connect 192.168.56.2:443 -CAfile ${CERT}/dhkim.com.crt
CONNECTED(00000003)
depth=0 C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
verify return:1
---
Certificate chain
 0 s:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
   i:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDYzCCAksCFDqFd/R0+wGNaqN2fIJQ9l6IYXjKMA0GCSqGSIb3DQEBCwUAMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTAeFw0yMjA0MjYwNjQ2NDNaFw0yMzA0MjYwNjQ2NDNaMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANDN
judmmqf88NP6KSWMkdrZzPUZpY6I2vqtzHDf0pxBvEcHyhwA76LYl5xfPL76USef
xgM7etNaRJ5sre3Rr1V3AaH2VWl9ERq2EPcMY1YSvodHmyPYIQxzRIF08sofoCdY
kQjpMcIkuGXdRuL8K7stlArpaYo0Urvkt0JOZSJGuxm2u7F+RrnXGpsC2s2U/A7X
DG43chRy93okuSXtL/9WlQjMiPxE4vuK7EUXGCD862vAmfN+sxiZfZLUBji3g88z
AY4He0PYnEakqdPtcTLXRi1K2i7KjIf5YOLKjOXXUHYAcRUGUe7J9FgW4Waq+L5j
HCHI3VULUoOqTwN18zECAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAoWVuIY3jCcWg
fGAT2quhcL570d/VFKusOOriuUdijN1fQGgud8I1zs/KddIDhRtFAozXJJMmBJAa
Z7PytRifOMbe4DkJtHFOJOHJdrA5OVDIAgrFhDy44rZvUBMRvbAfw1aDhJKkp7Ie
Anibtz+WFc3W9ys8BJ9T1utFnaU2k0V1Bj2d39fx114POpkAxOqY1PSZJVavuxPB
EM4FYb5DSeglYGZJUkUadC768YVpIZH0Sbitdk3qM9WLPh0ur2GIn5hRzdGrBYUz
kQOWdC1g/4y1wkGlaCn5TNtHdyrEfbI7Oer6uraCm24XpqhTFaYS0SJ9iz4zSC8X
5CU9g6AP9g==
-----END CERTIFICATE-----
subject=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

issuer=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 1548 bytes and written 400 bytes
Verification: OK
---
New, TLSv1.2, Cipher is ECDHE-RSA-AES256-GCM-SHA384
Server public key is 2048 bit
Secure Renegotiation IS supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
SSL-Session:
    Protocol  : TLSv1.2
    Cipher    : ECDHE-RSA-AES256-GCM-SHA384
    Session-ID: 2AB8B353A394D3FB1E6F0945DBA7939C5DBC2B0047FE43DDB607A7AE9F232900
    Session-ID-ctx:
    Master-Key: 37CE046D9DC270224D50D6644E1838F1CC44346B16AF5C6073C9F546DC753AB30BC06E20C13757B2676B31A28FBBCEEC
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 300 (seconds)
    TLS session ticket:
    0000 - 03 e5 eb fb 09 37 45 c8-9d 42 c5 8d a0 9c da 04   .....7E..B......
    0010 - 53 fa b5 8e bb d0 d2 2f-d2 90 11 b9 67 28 af 51   S....../....g(.Q
    0020 - f8 92 b3 25 af 3b 43 98-78 42 af 89 1e 6c b7 d8   ...%.;C.xB...l..
    0030 - ee bc d2 c5 cd 60 e3 ef-3c 8b 96 a2 83 57 2d f0   .....`..<....W-.
    0040 - 72 6a aa 03 9b ac ca bc-bf cc b8 2f ba d6 31 e9   rj........./..1.
    0050 - 74 37 90 d0 84 6c f8 2e-0d 20 46 1a 0c df ab a9   t7...l... F.....
    0060 - e0 be 5c 9a 44 e0 66 6a-60 b1 8d 82 55 2e 38 c7   ..\.D.fj`...U.8.
    0070 - 5c 7c 66 54 47 0d fe f2-54 18 4e 78 90 aa ac 11   \|fTG...T.Nx....
    0080 - 82 5c 00 42 46 10 88 23-4d f4 ce 6e db 1b 81 d2   .\.BF..#M..n....
    0090 - 45 45 95 18 35 f9 80 80-25 2d 43 4b b8 81 5c 8a   EE..5...%-CK..\.
    00a0 - 45 2d 16 32 84 f1 47 92-c0 46 c4 6a d2 3e f7 ad   E-.2..G..F.j.>..
    00b0 - d2 64 17 a4 2b 62 7d cf-e2 29 bd 98 7e 21 9f ca   .d..+b}..)..~!..
    00c0 - 42 c6 a7 3f 57 c4 b4 92-9a a0 d6 1f 21 3a 8d 15   B..?W.......!:..

    Start Time: 1651027020
    Timeout   : 7200 (sec)
    Verify return code: 0 (ok)
    Extended master secret: yes
---
```

> 인증서를 Server측 handshake 에 사용되도록 지정하여,
>
> `78 Line` `Verification: OK` 정상적으로 키 교환(exchange)이 완료된 것을 알 수 있습니다.

<br>


### (3). 사설 인증서 사용 (download ssl)

* 앞서 진행한것 처럼, `openssl` 으로 원격지의 SSL 인증서를 내려 받습니다.

```bash
$ openssl s_client -servername dhkim.com -connect 192.168.56.2:443 > ${CERT}/download_dhkim.com.crt
```


* 받은 인증서로 SSL 연결을 수행해봅니다.

```bash
$ openssl s_client -servername dhkim.com -connect 192.168.56.2:443 -CAfile ${CERT}/download_dhkim.com.crt
CONNECTED(00000003)
depth=0 C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
verify return:1
---
Certificate chain
 0 s:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
   i:C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDYzCCAksCFDfIh7j8xqsFYz9suq3XIC9rAG6PMA0GCSqGSIb3DQEBCwUAMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTAeFw0yMjA1MTAwOTQ4NDdaFw0yMzA1MTAwOTQ4NDdaMG4x
CzAJBgNVBAYTAktSMQ4wDAYDVQQIDAVTZW91bDESMBAGA1UEBwwJU2VvY2hvLWd1
MQ0wCwYDVQQKDARPU0NJMRgwFgYDVQQLDA9DbG91ZCBNaWdyYXRpb24xEjAQBgNV
BAMMCWRoa2ltLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALYY
RPC8/lh6TPsWmhqgtpb5GUAfODUahfkkklR0pUafCPpVyfAoBKzMcYgEU8kK0ETf
T8jF9LrforRAa6rrm7e2I3N93TzUgypRAdJeoFC1Eg1YpchHGHkoDVrMqMZdCjVZ
+2QR0E8B16RedzCY55ctb0dCHckoD4nnzwvm6HInpFK6DrZBxdbEh1Dr8hiEsWtH
bYeHGFWc/ugmAlVzuQLNevInKS9pUFglb7yxYpkVI4wf6C/Hyf0Wba34yBcGLtbr
cF32TJrp12wAq1D16jUX1fDwiiq6P9mo0Xxw2bza17PyzeV++i2DszRjhgh9A1RE
6A/ZX15gtgYY4Bsp4e8CAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAgwp7vJb24g6r
78VPi3UwEkgSRbSnc9yK2KlObc2xtwK5TbibeIPdbkw5vPj9tieCgNyvKfpWnIni
/CvDILdaRnAMcCbP2O3cNBK/xQDvL1pw3GMzWaZvPgqGNNQ1GOD5FzPnBXniOG8T
OsY54KG31zLp7/JslJ7CmtfFFXRRMMYIRXBMJdNNZE4n4j6+SNOdhFlxAqGevrzE
qKAndFkRsr//le62ddeegVZdiZiEZfbPNx3ebfs98VXV7HyvsDt3H/oRGXsBF1gl
DyqobfbdovazynOi/NHZN2JJEaZREVM7itozp26cIfmgEXwWkGEocPZOGMAQYDo2
5fq8KSWaKg==
-----END CERTIFICATE-----
subject=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

issuer=C = KR, ST = Seoul, L = Seocho-gu, O = OSCI, OU = Cloud Migration, CN = dhkim.com

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 1431 bytes and written 387 bytes
Verification: OK
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 2048 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 0 (ok)
---
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: A03B5C0C44A33E76139812885A5DA3FB2D93D30DAEB1FDD43573D441623E0D9E
    Session-ID-ctx:
    Resumption PSK: B6B80C4EAC340F04EE6DC74A4A24734B991646EFF0800527D5F2FDCA6EB0162F37B9864B22A1256497B024E97882B7B6
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 300 (seconds)
    TLS session ticket:
    0000 - 1f be 43 bb 42 73 6a cf-2a cb cc 05 fc 02 6d aa   ..C.Bsj.*.....m.
    0010 - c2 55 52 b8 15 1e a9 f7-bf bb 83 3d 92 9e 8d 9c   .UR........=....
    0020 - 04 74 0c 58 11 17 42 94-1b 1f 46 78 85 64 f2 69   .t.X..B...Fx.d.i
    0030 - 90 8c 77 3d e0 f0 0a 28-1e aa 82 2a 66 26 07 3a   ..w=...(...*f&.:
    0040 - 2d b1 4b 69 5e a2 32 e0-2e 4e 6c fe 3e f0 55 64   -.Ki^.2..Nl.>.Ud
    0050 - 1f 12 e8 df 93 75 2e 3b-5f 53 b2 d4 0b ce 7b c0   .....u.;_S....{.
    0060 - 28 a6 1a 93 a7 b8 73 44-2f 04 6a f1 38 ab a9 0e   (.....sD/.j.8...
    0070 - e0 a3 ef 16 1a a1 07 f4-6f e1 37 ca 8f d2 9d a8   ........o.7.....
    0080 - 11 31 0a 4c 8b 68 38 f1-7a 76 94 14 ba ed cb 1d   .1.L.h8.zv......
    0090 - a2 9e bc 2e ac 2a 6b f9-e1 67 f3 9a 78 c3 6f 89   .....*k..g..x.o.
    00a0 - 18 6a f6 ed 48 92 28 06-36 ec 31 e5 f6 ed e9 45   .j..H.(.6.1....E
    00b0 - a5 9b 81 f6 10 3a 11 77-00 e9 0c 02 51 e8 e7 39   .....:.w....Q..9
    00c0 - 4b b7 07 0c 67 ad 06 e8-90 ff 4d 39 d2 20 23 43   K...g.....M9. #C
    00d0 - c2 c6 f9 a0 44 66 f6 08-66 13 69 6c 8b ab 38 d8   ....Df..f.il..8.
    00e0 - a6 a2 76 b2 2d 3b 7e 11-8a b8 fe 86 6c 8d 9a d7   ..v.-;~.....l...

    Start Time: 1652243552
    Timeout   : 7200 (sec)
    Verify return code: 0 (ok)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK
---
Post-Handshake New Session Ticket arrived:
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: CEA4F8BF660A26FDA72552816D2D050AE8252ADC5D2D9E2771811AE98AB70FEF
    Session-ID-ctx:
    Resumption PSK: D0E73731976C0FF9F7A1A2FD6AAFB03470E1F9D75E4D5B263105448ABD589D1DCA7E71C64F7FC2CB2C510FF5D6136EB9
    PSK identity: None
    PSK identity hint: None
    SRP username: None
    TLS session ticket lifetime hint: 300 (seconds)
    TLS session ticket:
    0000 - 1f be 43 bb 42 73 6a cf-2a cb cc 05 fc 02 6d aa   ..C.Bsj.*.....m.
    0010 - 0a d4 b9 4d 53 d8 ab 95-34 49 ae 07 72 ae 7e 8f   ...MS...4I..r.~.
    0020 - 2b c7 a9 db 65 61 58 23-78 27 3a 61 92 97 82 49   +...eaX#x':a...I
    0030 - d8 f2 0d b8 34 b8 62 07-a7 53 1c 2c 66 2b bb 91   ....4.b..S.,f+..
    0040 - ad e2 21 dd 3d f6 69 cf-68 f2 2f c0 2f a5 c4 f8   ..!.=.i.h././...
    0050 - ab fe 26 7c 4c 3d 78 31-6f 24 dd 11 7e 45 85 cc   ..&|L=x1o$..~E..
    0060 - 2b 95 f5 21 8f 9c 04 b0-93 6b ba b1 e5 a5 ea 12   +..!.....k......
    0070 - 1d a5 37 d6 eb b0 d1 76-61 c2 34 6d 28 06 41 99   ..7....va.4m(.A.
    0080 - 92 e7 ad 59 ab a3 22 1d-9d 6a a9 f3 fa 92 da 32   ...Y.."..j.....2
    0090 - 4a 49 4a 11 87 0c a9 00-a3 83 74 2a 53 d4 46 36   JIJ.......t*S.F6
    00a0 - 95 45 5c e9 18 1c 45 c3-83 bf 65 5a e5 45 07 08   .E\...E...eZ.E..
    00b0 - e9 00 3f 49 ed 22 cf d2-78 46 6b a2 e7 fd d4 9e   ..?I."..xFk.....
    00c0 - 63 09 ce f1 05 f8 48 90-07 7e 41 c7 4b 80 cb 48   c.....H..~A.K..H
    00d0 - ab ed 29 35 c7 25 b1 09-80 b1 9e 6c 36 25 15 5d   ..)5.%.....l6%.]
    00e0 - 01 24 ee 24 00 62 10 e7-9b dd 22 3d 54 f0 01 19   .$.$.b...."=T...

    Start Time: 1652243552
    Timeout   : 7200 (sec)
    Verify return code: 0 (ok)
    Extended master secret: no
    Max Early Data: 0
---
read R BLOCK

HTTP/1.1 400 Bad Request
Date: Wed, 11 May 2022 04:32:34 GMT
Server: Apache
Content-Length: 226
Connection: close
Content-Type: text/html; charset=iso-8859-1

<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html><head>
<title>400 Bad Request</title>
</head><body>
<h1>Bad Request</h1>
<p>Your browser sent a request that this server could not understand.<br />
</p>
</body></html>
closed
```

> 원격지의 인증서로, SSL handshake를 시도하였고, `85 Line` 로그를 통해 정상적으로 처리된 것을 알 수 있습니다.

<br>


## 4.3 HttpUrlConnection (JAVA)

* 여기서는 JAVA 기반의 어플리케이션을 통해 원격지 서버와 SSL 통신을 수립해봅니다.
* 테스트를 위해 다음의 어플리케이션이 AP에 배포된다고 가정합니다.

```jsp
<%@ page contentType="text/html; charset=UTF-8" %>
<%@ page import="java.io.*" %>
<%@ page import="java.net.*" %>
<%
    URL url = new URL("https://dhkim.com/index.html".toString());
    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
    connection.setDoOutput(true);
    OutputStreamWriter osw = new OutputStreamWriter(connection.getOutputStream());
    try {
        osw.write("");
        osw.flush();
    } finally {
        if (osw != null) osw.close();
    }

    BufferedReader brin = new BufferedReader(new InputStreamReader(connection.getInputStream()));
    String resStr = null;
    StringBuffer resStrBuff = new StringBuffer();
    try {
          while ((resStr = brin.readLine()) != null) {
              resStrBuff.append(resStr);
          }
    } finally {
        if (brin != null) brin.close();
    }
    out.println(resStrBuff);
    System.out.println(resStrBuff);
%>
```

> 단순히, AP 호출 시 `https://dhkim.com/index.html` 을 호출하는 소스코드 입니다.

<br>


### (1). AP 호출하여 HTTPS 연결

* AP에 배포된 어플리케이션을 호출하면, HttpUrlConnection Class가 `https://dhkim.com/index.html`을 호출합니다.

  그러나, 원격지(requested target)와 SSL Handshake에 필요한 유효한 인증서가 없어(unable to find valid certi..) Exception 이 발생하였습니다.

```
Caused by: javax.net.ssl.SSLHandshakeException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target

Caused by: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

<br>


### (2). SSL 인증서 to Java Key Store 변환

* AP(Client; 호출자)에 SSL 인증서 Setup을 위해 JKS로 변환하는 과정이 필요합니다.

  JAVA 기반에서는 SSL 인증서를 JKS로 감싸주어야 이해할 수 있기 때문입니다.

```bash
$ cat ${CERT}/private.key ${CERT}/dhkim.com.crt ${CERT}/root.csr > ${CERT}/dhkim.com.pem
```

> 개인키, 서버 인증서, CSR 인증서를 하나의 `dhkim.com.pem` 파일로 합칩니다.


* 확장자를 pem 으로 만들었다고, 완성되는 것이 아닙니다.

  pkcs12 Format으로 변환 해주어야 합니다.

```bash
$ openssl pkcs12 -export -in ${CERT}/dhkim.com.pem -out ${CERT}/dhkim.com.p12
Enter pass phrase for /tmp/self_signed_cert/dhkim.com.pem: (dhkim)
Enter Export Password: (pkcs123456)
Verifying - Enter Export Password: (pkcs123456)
```

> private.key 암호인 `dhkim` 와
>
> p12 파일의 암호인 `pkcs123456` 을 차례대로 입력합니다.
>
> `pkcs12` Format은 하나의 단일 File에 여러개의 인증서를 묶을 수 있게 해줍니다.


* pkcs12 Format 파일을 JKS에 집어 넣습니다.

```bash
$ keytool -importkeystore -srcstoretype pkcs12 -srckeystore ${CERT}/dhkim.com.p12 -deststoretype jks -destkeystore ${CERT}/dhkim.com.jks
키 저장소 /tmp/self_signed_cert/dhkim.com.p12을(를) /tmp/self_signed_cert/dhkim.com.jks(으)로 임포트하는 중...
대상 키 저장소 비밀번호 입력: (jks123456)
새 비밀번호 다시 입력: (jks123456)
소스 키 저장소 비밀번호 입력: (pkcs123456)
1 별칭에 대한 항목이 성공적으로 임포트되었습니다.
임포트 명령 완료: 성공적으로 임포트된 항목은 1개, 실패하거나 취소된 항목은 0개입니다.

Warning:
JKS 키 저장소는 고유 형식을 사용합니다. "keytool -importkeystore -srckeystore /tmp/self_signed_cert/dhkim.com.jks -destkeystore /tmp/self_signed_cert/dhkim.com.jks -deststoretype pkcs12"를 사용하는 산업 표준 형식인 PKCS12로 이전하는 것이 좋습니다.
```

> dhkim.com.jks 암호인 `jks123456`와
>
> dhkim.com.p12 암호인 `pkcs123456` 을 차례대로 입력합니다.

<br>


### (3). JKS Setup 후 HTTPS 재연결

* 위에서 생성한 JKS를 AP에 Setup 합니다.

```bash
CERT=/tmp/self_signed_cert
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStoreType=JKS"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStore=${CERT}/dhkim.com.jks"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStorePassword=jks123456"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStore=${CERT}/dhkim.com.jks"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStorePassword=jks123456"
export JAA_OPTS
```


* AP에서 HttpUrlConnection을 통해 HTTPS WEB을 호출하면 에러가 여전히 발생하고 있습니다.

  아까와는 다른 에러 로그가 보입니다.

  `Cannot recover key`는 대게, SSL 인증서를 제공된 패스워드로 해독할 수 없어 발생합니다.

<br>

* 위에서 JKS, PKCS12 각기 다른 패스워드로 관리하기 위해 지정하였는데 에러가 발생했습니다.

  이 부분에서는 도움이 될 만한 힌트 등을 구글링으로 알 수가 없었습니다.

```
java.net.SocketException: java.security.NoSuchAlgorithmException: Error constructing implementation (algorithm: Default, provider: SunJSSE, class: sun.security.ssl.SSLContextImpl$DefaultSSLContext)
...
java.security.UnrecoverableKeyException: Cannot recover key
```

> `Cannot recover key` 는, dhkim.com.jks Keystore 에 추가한 개인키 인증서를 `jks123456` 값으로 해독할 수 없어 발생합니다.


* Keystore Password를 변경합니다.

```bash
$ keytool -storepasswd -keystore ${CERT}/dhkim.com.jks
키 저장소 비밀번호 입력: (jks123456)
새 keystore password: (dhkim123456)
새 keystore password 다시 입력: (dhkim123456)

Warning:
JKS 키 저장소는 고유 형식을 사용합니다. "keytool -importkeystore -srckeystore /tmp/self_signed_cert/dhkim.com.jks -destkeystore /tmp/self_signed_cert/dhkim.com.jks -deststoretype pkcs12"를 사용하는 산업 표준 형식인 PKCS12로 이전하는 것이 좋습니다.
```

> 생성한 keystore의 password를 `dhkim123456`으로 변경했습니다.


* Keystore 내에 저장된 인증서 Password를 변경합니다.

  `dhkim.com.jks` Keystore Password와 Keystore 내에 저장된 인증서의 Password를 동일하게 변경하는 작업입니다.

```bash
$ keytool -keypasswd -keystore ${CERT}/dhkim.com.jks -alias 1
키 저장소 비밀번호 입력: (dhkim123456)
<1>에 대한 키 비밀번호를 입력하십시오. (pkcs123456)
새 <1>에 대한 키 비밀번호: (dhkim123456)
새 <1>에 대한 키 비밀번호 다시 입력: (dhkim123456)

Warning:
JKS 키 저장소는 고유 형식을 사용합니다. "keytool -importkeystore -srckeystore /tmp/self_signed_cert/dhkim.com.jks -destkeystore /tmp/self_signed_cert/dhkim.com.jks -deststoretype pkcs12"를 사용하는 산업 표준 형식인 PKCS12로 이전하는 것이 좋습니다.
```

> `-alias 1` : 처음에 Keystore 내에 인증서(`dhkim.com.p12`)를 저장할 때, 별칭을 주지 않았으므로 기본값 1이 지정되었습니다.


* 다음과 같이 AP Setup 한 내용 중에, `Password` 를 변경합니다.

```bash
CERT=/tmp/self_signed_cert
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStoreType=JKS"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStore=${CERT}/dhkim.com.jks"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.keyStorePassword=dhkim123456"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStore=${CERT}/dhkim.com.jks"
export JAVA_OPTS="$JAVA_OPTS -Djavax.net.ssl.trustStorePassword=dhkim123456"
export JAVA_OPTS
```


* AP → HTTPS WEB 호출 시, STDOUT Log 또는, 웹 브라우저에 문제가 없고 결과물이 잘 나오는 것을 확인하였습니다.

```bash
Hello world<br>/tmp/htdocs_ssl/index.html
```

<br>


# 5. 마무리

SSL 인증서를 여러 환경에 적용해보고, `curl` 과 `openssl` 명령으로 검증을 수행해보았습니다.

이 테스트를 하게 된 계기는, 고객사의 SSL 인증서 교체 이후 검증 방식을 제대로 알고 있지 않아 준비해보게 되었습니다.

물론, 고객사의 이슈와는 전혀 다른 상황이 펼쳐지더라도. 때때로 SSL 인증 과정에 문제가 없는지를 확인할 필요성이 많기 때문에

저에게는 유용한 시간이 되었습니다.

이것으로 글을 마무리 하며, 다음 시간에는 Spring Security의 Session Fixation 을 이슈로 겪었던 사례를 가지고 찾아뵙도록 하겠습니다.
