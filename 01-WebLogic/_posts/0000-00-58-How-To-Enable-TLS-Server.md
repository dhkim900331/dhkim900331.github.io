---
date: 2022-12-23 08:46:50 +0900
layout: post
title: "[WebLogic] How to Enable TLS-Server"
tags: [WebLogic, TLS, SSL, Certificate]
typora-root-url: ..
---

# 1. 개요

WebLogic Server 14c 기준에서 Server 측에 TLS Protocol을 어떻게 다루는지 알아본다.



# 2. TLS 지원 정보

[WebLogic Server 14c 표준 Security 지원 정보](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/standards.html#GUID-9DA3FE17-6ABA-4380-B2AE-FCBB39E0B7EC) 에서 표준으로 지원하는 Security 항목을 확인할 수 있다.

* TLS 1.2 이상을 권장
* TLS 1.2 미만 버전에 대해서는 JDK에 의해 Disabled 될 수 있다.



[SSL/TLS 프로토콜 버전 지정](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/ssl_version.html) 에서 Protocol 인수를 살펴볼 수 있다.

* `weblogic.security.SSL.protocolVersion` : 활성화할 Protocol
* `weblogic.security.SSL.minimumProtocolVersion` : 위 Protocol에서 최소 버전 지정
* `weblogic.security.ssl.sslcontext.protocol`
* (Note) `$JAVA_HOME/jre/lib/security/java.security` 의 `jdk.tls.disabledAlgorithms` 에서 Protocol 기본값.



# 3. WLS에서 TLS 활성화

WebLogic Server 14c 기준으로는 TLS 1.2v 가 최소버전 으로 지정되어 있다.

아래 에서 그 기본값을 검증하고, 최소 버전 변경방법을 살펴본다.



## 3.1 TLSv1.2 (Default)

Self-Signed SSL Certificate 를 적용하였다.

openssl 명령어로 TLS 버전별로 확인을 간략히 해보면...



TLSv1.0

```shell
$ openssl s_client -connect wls.local:8441 -tls1
CONNECTED(00000003)
140159853406016:error:1409442E:SSL routines:ssl3_read_bytes:tlsv1 alert protocol version:ssl/record/rec_layer_s3.c:1544:SSL alert number 70
---
no peer certificate available
---
```



TLSv1.1

```shell
$ openssl s_client -connect wls.local:8441 -tls1_1
CONNECTED(00000003)
140675578558272:error:1409442E:SSL routines:ssl3_read_bytes:tlsv1 alert protocol version:ssl/record/rec_layer_s3.c:1544:SSL alert number 70
---
no peer certificate available
---
```



TLSv1.2

```shell
$ openssl s_client -connect wls.local:8441 -tls1_2
CONNECTED(00000003)
depth=0 DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
verify error:num=18:self signed certificate
verify return:1
depth=0 DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
verify return:1
---
Certificate chain
 0 s:DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
   i:DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDYzCCAkugAwIBAgIEeZa2YzANBgkqhkiG9w0BAQsFADBiMRMwEQYKCZImiZPy
...
```



TLSv1.3

```shell
$ openssl s_client -connect wls.local:8441 -tls1_3
CONNECTED(00000003)
depth=0 DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
verify error:num=18:self signed certificate
verify return:1
depth=0 DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
verify return:1
---
Certificate chain
 0 s:DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
   i:DC = KIS, C = KR, ST = ST, L = L, O = O, OU = OU, CN = KIS
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIDYzCCAkugAwIBAgIEeZa2YzANBgkqhkiG9w0BAQsFADBiMRMwEQYKCZImiZPy
...
```



기본적으로 TLSv1.2, TLSv1.3 이 활성화 되어 있다.

_이후 부터는 위 TLS 명령어의 출력결과를 생략하고, 성공 여부를 직접 기입한다._



## 3.2 TLSv1.0 (TLSv1.2 미만)

다음의 옵션을 적용한다.

```shell
-Dweblogic.security.SSL.minimumProtocolVersion=TLSv1
-Djava.security.properties=${DOMAIN_HOME}/java.security
```



`java.security`는 ${JAVA_HOME}/jre/lib/security/java.security 의 복제본이며, 다음처럼 편집한다.

```java.security
#jdk.tls.disabledAlgorithms=SSLv3, TLSv1, TLSv1.1, RC4, DES, MD5withRSA, \
jdk.tls.disabledAlgorithms=SSLv3, RC4, DES, MD5withRSA, \
    DH keySize < 1024, EC keySize < 224, 3DES_EDE_CBC, anon, NULL, \
    include jdk.disabled.namedCurves
```

_TLSv1, TLSv1.1_ 을 비활성 리스트에서 제거했다.



다음의 명령어로 TLSv1.0 ~ TLSv1.3 까지 정상 수행된다.

```shell
$ openssl s_client -connect wls.local:8441 -tls1
$ openssl s_client -connect wls.local:8441 -tls1_2
$ openssl s_client -connect wls.local:8441 -tls1_3
```

