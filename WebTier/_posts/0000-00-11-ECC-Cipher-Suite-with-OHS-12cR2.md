---
date: 2024-07-03 16:39:54 +0900
layout: post
title: "[WebTier/OHS] ECC Cipher Suite with OHS 12cR2"
tags: [WebTier, OHS, ECC, cipher, suite, ssl, tls]
typora-root-url: ..
---

# 1. Overview
Oracle HTTP Server 12.2.1.4 에서 ECC(Elliptic-curve cryptography)를 지원한다.


<br><br>

<br>

# 2. Descriptions
[Table H-1 SSLCipher Suite Tags](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/ohs-module-directives.html#GUID-C76BCA2A-9C28-4D16-9758-9346FBCF7512__CIHCEDCG) 에서 사용 가능한 Cipher suites 목록이 있다.

ECDSA, ECDHE와 같이 ECC 기반 Cipher suite를 사용할 수 있다.

<br>

특정 요구사항으로, X25519Kyber768 를 지원하는지에 대해서 논의한다면,

X25519는 ECC 기반 알고리즘이지만, 위 목록에 포함되어 있지 않고,

Kyber(Post-Quantum Cryptography) 또한 지원되지 않아 X25519Kyber768은 사용 불가하다.


<br><br>

<br>

# 3. References
Oracle HTTP Server 12cR2 버전에서 ECC(Elliptic Curve Cryptography)를 지원합니까? (Doc ID 3031719.1)