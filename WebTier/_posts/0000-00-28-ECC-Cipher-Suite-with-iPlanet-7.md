---
date: 2024-07-03 16:39:54 +0900
layout: post
title: "[WebTier/iPlanet] ECC Cipher Suite with iPlanet 7"
tags: [WebTier, iPlanet, ECC, cipher, suite, ssl, tls]
typora-root-url: ..
---

# 1. Overview
iPlanet 7 에서 ECC(Elliptic-curve cryptography)를 지원한다.

{{ site.content.br_big }}


# 2. Descriptions
[A.27.15 Elliptic Curve Cryptography Support](https://docs.oracle.com/cd/E18958_01/doc.70/e18789.pdf) ECC를 지원하고 있음을 알 수 있다.

[ssl3-tls-ciphers](https://docs.oracle.com/cd/E19146-01/821-1827/gcfbv/index.html) 에서 Cipher suites 목록을 확인한다.
{{ site.content.br_small }}
특정 요구사항으로, X25519Kyber768 를 지원하는지에 대해서 논의한다면,

X25519는 ECC 기반 알고리즘이지만, 위 목록에 포함되어 있지 않고,

Kyber(Post-Quantum Cryptography) 또한 지원되지 않아 X25519Kyber768은 사용 불가하다.

{{ site.content.br_big }}


# 3. References
iPlanet 7.X 버전에서 ECC(Elliptic Curve Cryptography)를 지원합니까? (Doc ID 3031765.1)