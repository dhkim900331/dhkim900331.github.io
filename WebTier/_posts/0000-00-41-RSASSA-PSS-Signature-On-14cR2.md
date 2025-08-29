---
date: 2025-04-30 23:47:19 +0900
layout: post
title: "[WebTier/OHS] RSASSA-PSS Signature On 14cR2 "
tags: [WebTier, OHS, ssl, RSA, PSS]
typora-root-url: ..
---

# 1. Overview

OHS 14cR2 (14.1.2) 에서는 [TLS 1.3 을 Support ](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/14.1.2/releasenotes-ohs/new.html#GUID-E393D5A5-86A2-4144-A705-90E74A58DDA2)하며,

TLS 1.3 표준에 따르면 RSASSA-PSS 서명을 필수/지원한다.

```
https://datatracker.ietf.org/doc/html/rfc8446

	The Transport Layer Security (TLS) Protocol Version 1.3

		1.2.  Major Differences from TLS 1.2

			Other cryptographic improvements were made, including changing the
				  RSA padding to use the RSA Probabilistic Signature Scheme
				  (RSASSA-PSS) 
```

<br>

OHS 에서도 사용 가능할까?

<br><br>


# 2. Descriptions

## 2.1 서명 알고리즘과 키 알고리즘

### **2.1.1 서명 알고리즘**

인증서의 서명을 검증할 때 사용되는 알고리즘


<br><br>


### **2.1.2 키 알고리즘**

데이터 암/복호화를 위해 사용해야 할 세션 키를 주고받을 때 사용되는 알고리즘


<br><br>


## 2.2 RSASSA-PSS

RSASSA-PSS 는 RSA에서 더 개량된 서명 알고리즘이며, PKCS#1 v2.1 표준 스펙에서 정의되어 있다.

PKCS#1 v2.1 은 TLS 1.3 을 말한다.

<br>

즉 TLS 1.3 에서 RSASSA-PSS 서명 알고리즘이 추가되었다.

또한, RSASSA-PSS 서명 알고리즘은, TLS 1.3 환경에서 필수로 제공되어야 한다.


<br><br>


## 2.3 TLS 1.2 에서의 RSASSA-PSS

TLS 1.2 에서는 아래와 같이 RSASSA-PSS 에 대해 설명한다.

	https://datatracker.ietf.org/doc/html/rfc5246
		
		The Transport Layer Security (TLS) Protocol Version 1.2
		
			Note that there are certificates that use algorithms and/or algorithm
			combinations that cannot be currently used with TLS.  For example, a
			certificate with RSASSA-PSS signature key (id-RSASSA-PSS OID in
			SubjectPublicKeyInfo) cannot be used because TLS defines no
			corresponding signature algorithm.

<br>

RSASSA-PSS 서명 알고리즘을 TLS 1.2 에서 지원하지 않는다고 요약할 수 있다.


<br><br>


## 2.4 TLS 1.3 에서의 RSASSA-PSS

TLS 1.3 에서는 RSA에 RSASSA-PSS 서명 알고리즘이 추가되었다는 것이다.

	https://datatracker.ietf.org/doc/html/rfc8446
	
		The Transport Layer Security (TLS) Protocol Version 1.3
	
			1.2.  Major Differences from TLS 1.2
	
				Other cryptographic improvements were made, including changing the
					  RSA padding to use the RSA Probabilistic Signature Scheme
					  (RSASSA-PSS) 

<br>

그런데, 다음과 같은 문구가 매우 어렵다고 느껴졌다.

	Implementations that advertise support for RSASSA-PSS (which is
	mandatory in TLS 1.3) MUST be prepared to accept a signature using
	that scheme even when TLS 1.2 is negotiated.  In TLS 1.2,
	RSASSA-PSS is used with RSA cipher suites.

<br>

문구만 보면

TLS 1.2 에서는 RSASSA-PSS 사용이 불가능한데, TLS 1.3 에서는 필수이며 사용이 가능하다.

Client가 TLS 1.2 를 사용하더라도, RSASSA-PSS 를 준비해야만(MUST) 한다고 알리고 있다.

<br>

즉, 시스템의 보안 강화를 위해

Client가 TLS 1.3을 요구하지 않는 환경이라고 하더라도

관리자는 TLS 1.3 (RSASSA-PSS 필수 사용해야 하는) 체계를 미리 준비해야 한다고 이해 된다.


<br><br>


## 2.5 Oracle HTTP Server 에서의 RSASSA-PSS

OHS 12cR2 는 mod_ossl (Oracle’s Secure Socket Layer) 을 사용하고 mod_ssl (OpenSSL) 과 유사하지만 다르다.

OHS 14cR2 (14.1.2) 는 OpenSSL 을 사용하도록 변경되었다.

여전히 Oracle Wallet을 통해 인증서를 구현해야 하지만, 기동 시점에 exportwallet 유틸리티를 통해 인증서가 추출되어 사용된다.

<br>

> + 참고 : How to Configure Self Signed Certificates for Standalone Oracle HTTP Server 14.1.2 Using Orapki (Doc ID 3065021.1)

<br>

[Table H-1 SSLCipher Suite Tags](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/14.1.2/administer-ohs/ohs-module-directives.html#GUID-C76BCA2A-9C28-4D16-9758-9346FBCF7512__CIHCEDCG) 에서 RSA 는 "authentication", "key exchange" 두 곳에서 사용된다.

즉, 서명 알고리즘으로도 사용되고 세션 키 교환으로도 사용 된다는 것이다. (주고받는 데이터 암/복호화는 다른 것임)

<br>

OpenSSL TLS 1.3 을 지원하는 OHS 14cR2 에서 RSA의 개량된 서명 알고리즘 'RSASSA-PSS' 또한 사용 가능해야 한다는 의미이다.

<br>

기본 인증서(Default wallet)이 적용된 OHS 14cR2 에 openssl 명령어로 확인 시, TLS1.2, TLS1.3 모두에서 RSA-PSS 서명 알고리즘이 사용된다.

```sh
$ openssl s_client -connect wls.local:10443 -tls1_3
...
Peer signature type: RSA-PSS
...


$ openssl s_client -connect wls.local:10443 -tls1_2
...
Peer signature type: RSA-PSS
...

```

<br>

위에서 알아본 바로는 TLS 1.2 표준 규격에 따라 실 사용은 불가능 한 것으로 이해했는데...

이 부분은 좀 더 살펴보고 있지만(관련 자료 확보를 위해),

TLS 1.2 추가로 릴리즈된 후속 버전들에서 RSASSA-PSS 를 사용가능하도록 업데이트 된 것으로 우선 보고 있다.


<br><br>

<br>

# 3. References

How to Convert PassWord Protected Wallet ewallet.p12 to auto_login_only Wallet cwallet.sso (Doc ID 2469964.1)

OHS Fails To Start With "Cannot open an encrypted wallet file" When Signature Algorithm in Wallet is RSASSA-PSS ([Doc ID 2127361.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=2127361.1)) 

[14.1.2]Oracle HTTP Server Fails to Start with Error "mod_ossl: Could not export SSLWallet(s)!" (Doc ID 3065044.1)

How to Configure Self Signed Certificates for Standalone Oracle HTTP Server 14.1.2 Using Orapki (Doc ID 3065021.1)
