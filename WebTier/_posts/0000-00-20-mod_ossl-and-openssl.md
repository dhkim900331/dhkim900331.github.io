---
date: 2023-08-04 08:47:48 +0900
layout: post
title: "[WebTier/OHS] mod_ossl 과 openssl"
tags: [WebTier, OHS, openSSL, mod_ossl	]
typora-root-url: ..
---

# 1. Overview

OHS가 설치된 시스템의 openSSL 을 업그레이드 해도 괜찮은가?

mod_ossl 모듈이 영향이 생기는게 아닌가?



# 2. Descriptions

Oracle에서 개발한 mod_ossl Module은 기능적으로 Apache의 mod_ssl Module과 유사하다.

다만, mod_ossl Module은 RSA security technology를 기반으로 하는 Oracle의 Secure Socket Layer를 사용하고,

mod_ssl Module은 OpenSSL 에서 제공하는 암호화 Engine을 사용한다.

그래서, mod_ossl Module은 OpenSSL 을 사용하거나 관계가 있지 않다.

> [mod_ossl Module—Enables Cryptography (SSL)](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/under_mods.html#GUID-9436C934-4A4F-4BB1-93CB-5FAFF2B5757E) 를 참고하시기 바랍니다.



그리고 mod_security2 Module 은 기본적으로 OHS에 함께 포함되어 배포된다.

mod_security2 Module은 OpenSSL libraries 를 사용한다.

이에 따라 OHS 설치 시에, 최소 설치 요구 조건으로 OpenSSL 을 요구한다.

> 예시로, [x86-64 Oracle Linux 9 (UL0+) and Red Hat Linux 9 (UL0+)](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-37C51062-3732-4A4B-8E0E-003D9DFC8C26__LINUX9) Platform 에 필요한 Package lists 를 참고하시기 바랍니다.



mod_security2 Module을 사용하는 경우, OpenSSL 상위 Version과의 호환성에 대해서 자료가 필요할 수 있지만

타사 Library 이므로 이에 대해서 정리된 자료가 Oracle에는 없다.

mod_security2 Module은 http://www.modsecurity.org/documentation.html 참고한다.



## 3. References

**mod_ossl Module과 openSSL Library와의 관계 (Doc ID 2965344.1)**
