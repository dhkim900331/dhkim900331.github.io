---
date: 2023-08-04 08:47:48 +0900
layout: post
title: "[WebTier/OHS] mod_ossl 과 openssl"
tags: [WebTier, OHS, openSSL, mod_ossl	]
typora-root-url: ..
---

# 1. Overview

Oracle HTTP Server(이하 OHS)가 설치된 시스템의 openSSL 을 업그레이드 해도 괜찮은가?

mod_ossl 모듈에 어떠한 영향이 생기는게 아닌가?


<br><br>


# 2. Descriptions

## 2.1 ~ OHS 12.2.1.4

OHS 12.2.1.4 버전 까지는

Oracle에서 개발한 mod_ossl Module은 기능적으로 Apache의 mod_ssl Module과 유사하다.

다만, mod_ossl Module은 RSA security technology를 기반으로 하는 Oracle의 Secure Socket Layer를 사용하고,

mod_ssl Module은 OpenSSL 에서 제공하는 암호화 Engine을 사용한다.

그래서, mod_ossl Module은 OpenSSL 을 사용하거나 관계가 있지 않다.

> [mod_ossl Module—Enables Cryptography (SSL)](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/under_mods.html#GUID-9436C934-4A4F-4BB1-93CB-5FAFF2B5757E) 를 참고


<br><br>

<br>


## 2.2 OHS 14.1.2 ~

OHS 14.1.2 버전 부터는

mod_ossl 과 mod_ssl Module 모두 동일한 OpenSSL 암호화 엔진을 사용한다.

> [mod_ossl Module—Enables Cryptography (SSL)](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/14.1.2/administer-ohs/under_mods.html#GUID-9436C934-4A4F-4BB1-93CB-5FAFF2B5757E) 를 참고

<br>

이를 위해 OpenSSL 3.0.15 이 요구 된다.

>  [Licensing Information User Manual for Oracle HTTP Server 14c (14.1.2.0.0)](https://docs.oracle.com/en/middleware/fusion-middleware/14.1.2/ohslc/index.html) 참고


<br><br>


## 2.3 mod_security2

그리고 관련성이 있는 mod_security2 Module에 대해서도 잠깐 설명을 해보자면,

이 Module은 OpenSSL libraries 를 사용하며 OHS에 함께 포함되어 배포된다.

이에 따라 OHS 설치 시에, 최소 설치 요구 조건으로 OpenSSL 을 요구한다.

> 예시로, [x86-64 Oracle Linux 9 (UL0+) and Red Hat Linux 9 (UL0+)](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-37C51062-3732-4A4B-8E0E-003D9DFC8C26__LINUX9) Platform 에 필요한 Package lists 를 참고

<br>

mod_security2 Module을 사용하는 경우, OpenSSL 상위 Version과의 호환성에 대해서 자료가 필요할 수 있지만

타사 Library 이므로 이에 대해서 정리된 자료가 Oracle에는 없다.

> mod_security2 Module은 https://modsecurity.org/ 참고

<br><br>


## 3. References

**mod_ossl Module과 openSSL Library와의 관계 (KB547891)**
