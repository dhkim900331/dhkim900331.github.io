---
date: 2023-08-24 09:33:44 +0900
layout: post
title: "[WebTier/OHS] How To Disable Weak SSLCipherSuite"
tags: [WebTier, OHS, ossl, cipher, ssl, suite]
typora-root-url: ..
---

# 1. Overview

OHS 12.2.1.4 SSLCipherSuite 취약점 제거 방법


<br><br>


# 2. Descriptions

nmap으로 OHS 12.2.1.4 SSLCipherSuite 취약점을 검진하면 다음과 같이 조사된다.

```bash
$ nmap -p 10443 --script ssl-enum-ciphers wls.local

PORT      STATE SERVICE
10443/tcp open  unknown
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_RSA_WITH_AES_128_GCM_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_GCM_SHA384 (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048) - A
|     compressors:
|       NULL
|     cipher preference: server
|_  least strength: A
```


TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048),

TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048)

위 2개의 Cipher Suite는 ssl.conf에서 다음 2개로 확인된다.

SSL_RSA_WITH_AES_128_CBC_SHA,

SSL_RSA_WITH_AES_256_CBC_SHA

<br>

위 취약점 2개만을 제거할 것이라면, 아래의 패치 과정 없이 단지 아래 2개를 제거하면 된다.

TLS와 SSL은 의미차이가 없으며, 단지 Spelling이 상이할 뿐이므로 이러한 사실을 염두해두어야 한다.

<br>

`Patch 35577558 (OHS BUNDLE PATCH 12.2.1.4.230707)` 패치를 적용,

`Patch 35577558 (OHS BUNDLE PATCH 12.2.1.4.230707)` 패치를 적용,

`SSLCipherSuite TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` 를 적용하면

<br>

```bash
$ nmap -p 10443 --script ssl-enum-ciphers wls.local

PORT      STATE SERVICE
10443/tcp open  unknown
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|     compressors:
|       NULL
|     cipher preference: server
|_  least strength: A
```


의도한 대로, 적용된다.

nmap 또한 third party이므로 nmap에서 응답할 수 있는 CipherSuite 항목에 따라 결과가 다를 수 있다.


<br><br>


# 3. References

**Cumulative README Post-Install Steps for Oracle HTTP Server 12.2.1.4 Bundle Patches (Doc ID 2743971.1)**
