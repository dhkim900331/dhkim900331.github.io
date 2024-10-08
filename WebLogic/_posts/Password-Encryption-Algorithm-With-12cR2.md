---
layout: post
title: "[WebLogic] Password Encryption Algorithm With 12cR2"
tags: [Middleware, WebLogic, encryption, algorithm, aes]
typora-root-url: ..
---

# 1. Overview
WLS 12.2.1.4 (12cR2) 에서 지원/사용 가능한 암호화 알고리즘

{{ site.content.br_big }}

# 2. Descriptions
[Security](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/notes/whatsnew.html#GUID-15E21252-21B2-4883-8E62-F6F30BF7576D) 에서 'AES 256-Bit Encryption Used in New Domains'

Docs link 오류로 인해 'AES 256-Bit Encryption Used in New Domains' 직접 링크 이동에 문제가 있어 보인다.

위 내용에 따르면, 12.2.1.4 Release 부터 새로 생성되는 도메인에 대해 AES-256 bit의 암호화를 사용하며, 이전 도메인은 AES-128 을 사용하게 된다.

12.2.1.4 부터 AES-258 사용에 대해 변경 가능한 방법은 안내되지 않고 있으므로,

도메인 구성 내 설정이나 런타임 시 모든 암호화 구간은 AES-258을 사용하게 된다.

{{ site.content.br_big }}

# 3. References
위 컨텐츠 내에 소개됨.