---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebLogic] HTTP cookies are not isolated between different ports"
tags: [Middleware, WebLogic, Session, Cookie, Clustering]
typora-root-url: ..
---

# 1. Overview

동일한 JSESSIONID를 Read/Update 하는 서로 다른 Application이 서로 다른 Server에서 서비스 될 때, 문제점


<br><br>



# 2. Descriptions

Hello와 World라는 서로 다른 Application이 있지만, JSESSIONID는 동일하고,

이 두 App은 업무 연관성이 있어 내부적으로 서로를 호출하는 Link가 있다.

<br>

Hello는 `http://<same-url>:3030` , World는 `http://<same-url>:5050` 에서 서비스 된다.

<br>

사용자가 Hello 서비스 내에서, 특정 Link를 눌러 World로 이동하게 되면,

각 서비스 앞에 있는 OHS Web이 브라우저에 저장된 Cookie를 읽는다.

> Cookie는 Site-Domain-URL 기반 및 Context-root 기반에 저장 되는데, 위는 same-url 이기 때문에 서로의 Cookie가 간섭받는다.

<br>

OHS는 다른 WLS의 JVMID (World 서비스의 OHS는 Hello 서비스의 WLS를 모른다.) 를 모르므로,

Plugin default algorithm에 의해, Round Robin 방식으로 Random한 World WLS로 Proxies 한다.

World WLS는 JVMID를 Set-Cookie로 덮어 씌운다.

<br>

이러한 일련의 과정들로 인해, 두 서비스간에 호출하게 되면 요청이 Sticky 하지 못하고 계속 각자(Hello, World) 내에서 Round robin 하게 된다.

<br>

두 Application을 서비스하는 Hello와 World의 WLS들은 Coherence Web으로 HTTP Session을 공유하여 쓰고,

Application의 JSESSIONID는 통일시킴으로써, 동일한 Session을 다루려고 설계된 것이다.

<br>

[RFC-6265 의 8.5.  Weak Confidentiality](https://www.rfc-editor.org/rfc/rfc6265#section-8.5)에 따르면,

```
Cookies do not provide isolation by port.
If a cookie is readable by a service running on one port,
the cookie is also readable by a service running on another port of the same server.

If a cookie is writable by a service on one port,
the cookie is also writable by a service running on another port of the same server.

For this reason, servers SHOULD NOT both run mutually distrusting services on different ports of the same host and use cookies to store security-sensitive information.
```

Port 구분을 하지 못하기 때문에, `<same-url>` 아래 Session이 Overwrote 된 것이다.

<br>

두 Application이 서로 다른데, EAR 등으로 묶지 않고 Http Session을 공유하고자 한 것의 결과이다.

두 Application을 끝끝내 EAR 등으로 묶지 않고, `<same-url>`을 다르게 한다고 해도, Cookie가 다른 URL에 업데이트 할 방법이 없으므로

sub-domain 방식을 쓰거나, 포기하고 EAR을 사용해야 한다.


<br><br>



# 3. References

내용에 포함됨
