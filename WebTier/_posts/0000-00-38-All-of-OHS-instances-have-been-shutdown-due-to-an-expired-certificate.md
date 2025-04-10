---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebTier/OHS] All of OHS instances have been shutdown due to an expired certificate"
tags: [WebTier, OHS, SSL, mod_dms]
typora-root-url: ..
---

# 1. Overview

특정 시점에 OHS 인스턴스가 모두 종료되었다.

당시 특이점은, 관리자는 특별한 작업을 하지 않았다는 것이고 Default wallet 인증서가 만료되었다는 것이다.

인증서가 만료되면 OHS 인스턴스가 종료될 수 있는것인가?

<br>

# 2. Descriptions

고객은 OHS SSL 서비스가 업무에 필요치 않아 활용하고 있지 않았다.

다만, OHS 인스턴스의 Health check를 하는 admin.conf 구성 요소 때문에 기본적으로 SSL 기능이 활성화 되어 있다.

> OHS 12.2.1.4 의 특정 minor release 부터 HTTP -> HTTPS 로 변경된 것으로 보인다.

<br>

admin.conf에는 mod_dms 모듈이 OHS Instance와 Nodemanager간의 Health check에 응답하는 역할을 수행하는데,

이때 SSL Protocol을 사용한다.

<br>

처음 설명대로 고객은 SSL 서비스가 필요 없지만, admin.conf에서 Default Wallet을 사용하고 있으며,

Wallet에 포함된 기본 인증서가 만료가 되는 시점이 마침 도래했다.

<br>

이후 SSL Handshake failure due to the expired certificate 이슈로 인해, Nodemanager는 해당 OHS instance가 응답을 제때 하지 못한다고 인식.

Nodemanager의 기본 동작인, OHS instance를 restart 한다.

<br>

이는 쉽게 예상할 수 없지만, 운영 서버에서 만료될 수 있는 기본 인증서를 방치 및 관리하지 못한 사용자의 책임에 있다.


<br><br>


# 3. References

<br>

